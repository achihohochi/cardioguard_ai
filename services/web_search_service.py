"""
Web Search Service
Search for legal/court information about healthcare providers.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import WEB_SEARCH_ENABLED, WEB_SEARCH_CACHE_DURATION, CACHE_DIR


class WebSearchService:
    """Service for searching legal/court information about providers."""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR / "web_search"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None
        self.enabled = WEB_SEARCH_ENABLED
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_cache_path(self, search_key: str) -> Path:
        """Get cache file path for search key."""
        # Sanitize search key for filename
        safe_key = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in search_key)
        return self.cache_dir / f"search_{safe_key[:50]}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False
        
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age.total_seconds() < WEB_SEARCH_CACHE_DURATION
    
    async def search_provider_legal_info(
        self, 
        provider_name: str, 
        npi: str, 
        specialty: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for legal/court information about provider."""
        if not self.enabled:
            logger.info("Web search disabled, skipping")
            return {"legal_results": [], "searches_performed": 0}
        
        # Create search key for caching
        search_key = f"{provider_name}_{npi}_{specialty or ''}"
        cache_path = self._get_cache_path(search_key)
        
        # Check cache first
        if self._is_cache_valid(cache_path):
            logger.info(f"Using cached web search results for {provider_name}")
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        
        try:
            # Build search queries
            queries = self._build_search_queries(provider_name, npi, specialty, location)
            
            # Perform searches in parallel (limited to 5 queries)
            search_tasks = []
            for query in queries[:5]:  # Limit to 5 searches
                search_tasks.append(self._perform_search(query))
            
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and deduplicate results
            all_results = []
            for result in search_results:
                if isinstance(result, Exception):
                    logger.warning(f"Search failed: {result}")
                    continue
                if isinstance(result, list):
                    all_results.extend(result)
            
            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            response_data = {
                "legal_results": unique_results,
                "searches_performed": len([r for r in search_results if not isinstance(r, Exception)]),
                "provider_name": provider_name,
                "npi": npi
            }
            
            # Cache the results
            try:
                with open(cache_path, 'w') as f:
                    json.dump(response_data, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to cache web search results: {e}")
            
            logger.info(f"Web search completed: {len(unique_results)} unique results for {provider_name}")
            return response_data
            
        except Exception as e:
            logger.warning(f"Web search failed for {provider_name}: {e}")
            return {
                "legal_results": [],
                "searches_performed": 0,
                "error": str(e)
            }
    
    def _build_search_queries(
        self, 
        provider_name: str, 
        npi: str, 
        specialty: Optional[str],
        location: Optional[str]
    ) -> List[str]:
        """Build search queries for legal information."""
        queries = []
        
        # Clean provider name
        clean_name = provider_name.strip()
        
        # Strategy 1: Full name + legal keywords
        queries.append(f'"{clean_name}" convicted healthcare fraud')
        queries.append(f'"{clean_name}" lawsuit healthcare')
        queries.append(f'"{clean_name}" court judgment')
        
        # Strategy 2: Name + specialty + legal keywords
        if specialty:
            queries.append(f'"{clean_name}" {specialty} malpractice')
            queries.append(f'"{clean_name}" {specialty} criminal')
        
        # Strategy 3: NPI + legal keywords
        queries.append(f'NPI {npi} legal court')
        queries.append(f'NPI {npi} lawsuit judgment')
        queries.append(f'National Provider Identifier {npi} fraud')
        
        # Strategy 4: Name + location + legal (if location available)
        if location:
            queries.append(f'"{clean_name}" {location} convicted')
            queries.append(f'"{clean_name}" {location} lawsuit')
        
        # Strategy 5: Pending/alleged cases
        queries.append(f'"{clean_name}" pending charges healthcare')
        queries.append(f'"{clean_name}" alleged fraud')
        
        return queries
    
    async def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a single web search using DuckDuckGo."""
        try:
            # Use DuckDuckGo HTML search (free, no API key required)
            session = await self._get_session()
            
            # DuckDuckGo search URL
            search_url = "https://html.duckduckgo.com/html/"
            
            params = {
                "q": query,
                "kl": "us-en"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            async with session.get(
                search_url, 
                params=params, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_duckduckgo_results(html, query)
                else:
                    logger.warning(f"DuckDuckGo search returned status {response.status}")
                    return []
                    
        except asyncio.TimeoutError:
            logger.warning(f"Web search timeout for query: {query}")
            return []
        except Exception as e:
            logger.warning(f"Web search error for query '{query}': {e}")
            return []
    
    def _parse_duckduckgo_results(self, html: str, query: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML search results."""
        results = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # DuckDuckGo result structure
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs[:10]:  # Limit to top 10 results
                try:
                    title_elem = div.find('a', class_='result__a')
                    snippet_elem = div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        snippet = ""
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)
                        
                        if title and url:
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                                "query": query
                            })
                except Exception as e:
                    logger.debug(f"Error parsing result: {e}")
                    continue
                    
        except ImportError:
            # Fallback: simple text extraction if BeautifulSoup not available
            logger.warning("BeautifulSoup not available, using basic parsing")
            # Basic regex-based extraction as fallback
            import re
            url_pattern = r'href="([^"]+)"'
            urls = re.findall(url_pattern, html)
            for url in urls[:10]:
                if 'duckduckgo.com' not in url:
                    results.append({
                        "title": "Search Result",
                        "url": url,
                        "snippet": "",
                        "query": query
                    })
        except Exception as e:
            logger.warning(f"Error parsing DuckDuckGo results: {e}")
        
        return results
