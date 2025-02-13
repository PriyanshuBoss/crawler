import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Set, Dict, Optional, Tuple
from collections import defaultdict
from rich.console import Console
import json
from aiohttp import TCPConnector
from concurrent.futures import ThreadPoolExecutor
from asyncio import Semaphore
from rich.table import Table
from config import CrawlerConfig

class UrlsFetcher:
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.visited_categories: Dict[str, Set[str]] = defaultdict(set)
        self.product_urls: Dict[str, Set[str]] = defaultdict(set)
        self.console = Console()
        self.semaphore = Semaphore(config.max_concurrent_requests)
        self.session: Optional[aiohttp.ClientSession] = None
        self.visited_urls: Dict[str, Set[str]] = defaultdict(set)
        

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            connector = TCPConnector(
                limit=self.config.max_connections_per_host,
                limit_per_host=self.config.max_connections_per_host,
                ttl_dns_cache=300
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                }
            )
        return self.session

    async def fetch_url(self, url: str, retry_count: int = 0) -> Optional[str]:
        """Fetch URL with retry logic and delay"""
        
        async with self.semaphore:
            
            try:
                if self.config.request_delay > 0:
                    await asyncio.sleep(self.config.request_delay)
                
                session = await self.get_session()
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    
                    elif response.status == 429 and retry_count < self.config.max_retries:
                        await asyncio.sleep(2 ** retry_count)
                        return await self.fetch_url(url, retry_count + 1)
                    
            
            except Exception as e:
                
                if retry_count < self.config.max_retries:
                    await asyncio.sleep(2 ** retry_count)
                    return await self.fetch_url(url, retry_count + 1)
            
            return None

    async def process_page(self, domain: str, page_url: str) -> Tuple[Set[str], List[str], List[str]]:
        """Process a single page and return found product URLs, subcategory URLs, and pagination URLs."""
        
        content = await self.fetch_url(page_url)
        
        if not content:
            return set(), [], []

        products = set()
        subcategories = set()
        pagination_links = set()
        
        with ThreadPoolExecutor(max_workers=self.config.num_workers) as executor:
            loop = asyncio.get_event_loop()
            soup = await loop.run_in_executor(executor, BeautifulSoup, content, 'html.parser')

            # Extract all links from the page
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                
                full_url = urljoin(f"https://{domain}", href)

                if self.is_product_url(full_url):
                    products.add(full_url)

                
                elif self.is_category_url(full_url) and full_url not in self.visited_categories[domain]:
                    subcategories.add(full_url)

                if self.is_pagination_url(full_url):
                    
                    pagination_links.add(full_url)

       
        if self.config.verbose:
            self.console.print(f"[yellow]Found {len(subcategories)} subcategories and {len(pagination_links)} pagination links on {page_url}[/yellow]")

        return products, list(subcategories), list(pagination_links)


    def is_product_url(self, url: str) -> bool:
        return any(re.search(pattern, url, re.IGNORECASE) 
                  for pattern in self.config.product_patterns)

    def is_category_url(self, url: str) -> bool:
        return any(re.search(pattern, url, re.IGNORECASE) 
                  for pattern in self.config.category_patterns)
    
    def is_pagination_url(self, url: str) -> bool:
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in self.config.pagination_patterns)
    
        

    async def crawl_category_pages(self, domain: str, start_url: str, depth: int = 0):
        """Crawl category pages, including subcategories and pagination links."""
        
        # Stop crawling if already visited or depth limit reached
        if start_url in self.visited_categories[domain] or depth > self.config.max_depth:
            return
        
        self.visited_categories[domain].add(start_url)

        products, subcategories, pagination_links = await self.process_page(domain, start_url)
        self.product_urls[domain].update(products)

        
        if self.config.verbose:
            self.console.print(f"[green]Products found: {len(products)}, Subcategories: {len(subcategories)}, Pagination links: {len(pagination_links)}[/green]")

        if depth < self.config.max_depth and subcategories:
            subcategory_tasks = []
            remaining_pages = self.config.max_pages_per_domain - len(self.visited_categories[domain])

            for page_url in subcategories[:remaining_pages]:
                if page_url not in self.visited_categories[domain]:
                    subcategory_tasks.append(self.crawl_category_pages(domain, page_url, depth + 1))

            if subcategory_tasks:
                await asyncio.gather(*subcategory_tasks)

        if pagination_links:
            pagination_tasks = []
            
            for page_url in pagination_links:
                
                if page_url not in self.visited_categories[domain]:  
                    pagination_tasks.append(self.crawl_category_pages(domain, page_url, depth))

            if pagination_tasks:
                await asyncio.gather(*pagination_tasks)


    async def process_batch(self, domain: str, urls: List[str]):
        """Process a batch of URLs concurrently"""
        tasks = []
        
        for url in urls:
            
            if url not in self.visited_categories[domain]:
                tasks.append(self.crawl_category_pages(domain, url))
        
        if tasks:
            await asyncio.gather(*tasks)

    async def crawl_domain(self, domain: str):
        """Crawl a single domain"""
        self.console.print(f"[yellow]Starting crawl of domain:[/yellow] {domain}")
        
        domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        base_url = f"https://{domain}"

        if base_url in self.visited_urls[domain]:
            return
        
        content = await self.fetch_url(base_url)
        
        if not content:
            return

        with ThreadPoolExecutor(max_workers=self.config.num_workers) as executor:
            loop = asyncio.get_event_loop()
            soup = await loop.run_in_executor(executor, BeautifulSoup, content, 'html.parser')
            
            category_urls = set()
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                
                if self.is_category_url(full_url):
                    category_urls.add(full_url)

        category_batches = [list(category_urls)[i:i + self.config.batch_size] 
                          for i in range(0, len(category_urls), self.config.batch_size)]
        
        for batch in category_batches:
            await self.process_batch(domain, batch)

    async def crawl_domains(self, domains: List[str]):
        """Crawl multiple domains concurrently"""
        tasks = [self.crawl_domain(domain) for domain in domains]
        await asyncio.gather(*tasks)
        
        if self.session:
            await self.session.close()

    def print_results(self):
      
        table = Table(title="Discovered Product URLs")
        table.add_column("Domain", style="cyan")
        table.add_column("Product URLs", style="green")
        table.add_column("Count", justify="right", style="magenta")
        
        for domain, urls in self.product_urls.items():
            url_list = "\n".join(sorted(urls))
            table.add_row(domain, url_list, str(len(urls)))
        
        self.console.print(table)

    def save_results(self, output_file: str):
       
        results = {domain: list(urls) for domain, urls in self.product_urls.items()}
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.console.print(f"[green]Results saved to:[/green] {output_file}")
