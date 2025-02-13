from dataclasses import dataclass
import multiprocessing
from typing import Optional, List

@dataclass
class CrawlerConfig:
    """Configuration for the crawler"""
    max_pages_per_domain: int = 50
    max_concurrent_requests: int = 10
    max_connections_per_host: int = 10
    batch_size: int = 50
    request_delay: float = 0.5
    timeout: int = 5
    max_retries: int = 2
    verbose: bool = True
    num_workers: int = multiprocessing.cpu_count()
    product_patterns: Optional[List[str]] = None
    category_patterns: Optional[List[str]] = None
    pagination_patterns: Optional[List[str]] = None
    
    max_depth=3 

    def __post_init__(self):
        
        if self.product_patterns is None:
            self.product_patterns = [
                r'/product[s]?/',
                r'/item/',
                r'/p/',
                r'/dp/',
                r'-p-\d+',
                r'/[^/]+/[^/]+/[^/]+-\d+/buy$',
                r'/\d+/buy$',
          
            ]
        
        if self.category_patterns is None:
            self.category_patterns = [
                r'/category/',
                r'/c/',
                r'/collections?/',
                r'/shop/',
                r'/[^/]+/[^/]+$'
            ]

        if self.pagination_patterns is None:
            self.pagination_patterns = [
                    r'page=(\d+)',
                    r'p=(\d+)',
                    r'/page/(\d+)',
                    r'/p/(\d+)',
                    r'offset=(\d+)',
                    r'[\?&]page=(\d+)'
                ]