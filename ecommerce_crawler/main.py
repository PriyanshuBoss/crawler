import asyncio
from config import CrawlerConfig
from fetcher import UrlsFetcher
import time
from constants import DOMAINS, RESULT_FILE

async def main():
    start_time = time.time()
    
    config = CrawlerConfig(
        max_concurrent_requests=50,
        max_connections_per_host=20,
        batch_size=100,
        request_delay=0.2,
        verbose=True
    )
    
    domains = DOMAINS
    
    crawler = UrlsFetcher(config)
    
    await crawler.crawl_domains(domains)
    
    crawler.print_results()
    crawler.save_results(RESULT_FILE)
    
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
