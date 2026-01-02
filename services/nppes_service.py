"""
NPPES Registry Service
Integration with CMS NPPES (National Plan and Provider Enumeration System) API.
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import NPPES_API_URL, NPPES_CACHE_DURATION, CACHE_DIR


class NPPESDataService:
    """Service for accessing NPPES provider registry."""
    
    def __init__(self):
        self.api_url = NPPES_API_URL
        self.cache_dir = CACHE_DIR / "nppes"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_cache_path(self, npi: str) -> Path:
        """Get cache file path for NPI."""
        return self.cache_dir / f"nppes_{npi}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False
        
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age.total_seconds() < NPPES_CACHE_DURATION
    
    async def get_provider_details(self, npi: str) -> Dict:
        """Get provider details from NPPES registry."""
        cache_path = self._get_cache_path(npi)
        
        # Check cache first
        if self._is_cache_valid(cache_path):
            logger.info(f"Using cached NPPES data for NPI {npi}")
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        
        # Fetch from API
        try:
            session = await self._get_session()
            
            params = {
                "number": npi,
                "version": "2.1",
                "pretty": "true"
            }
            
            async with session.get(self.api_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    processed_data = self._process_nppes_response(data, npi)
                    
                    # Cache the result
                    try:
                        with open(cache_path, 'w') as f:
                            json.dump(processed_data, f, indent=2)
                    except Exception as e:
                        logger.warning(f"Failed to cache NPPES data: {e}")
                    
                    return processed_data
                else:
                    error_msg = f"NPPES API error: {response.status}"
                    logger.error(error_msg)
                    return {"error": error_msg}
                    
        except asyncio.TimeoutError:
            error_msg = "NPPES API timeout"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"NPPES connection failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _process_nppes_response(self, api_response: Dict, npi: str) -> Dict:
        """Process NPPES API response."""
        if api_response.get('result_count', 0) == 0:
            return {"error": f"Provider not found in NPPES registry: {npi}"}
        
        provider_data = api_response['results'][0]
        basic_info = provider_data.get('basic', {})
        addresses = provider_data.get('addresses', [])
        
        # Find practice location address
        practice_address = {}
        for addr in addresses:
            if addr.get('address_purpose') == 'LOCATION':
                practice_address = addr
                break
        
        # Extract taxonomies
        taxonomies = []
        for tax in provider_data.get('taxonomies', []):
            taxonomies.append({
                "code": tax.get('code', ''),
                "description": tax.get('desc', ''),
                "license": tax.get('license', ''),
                "state": tax.get('state', '')
            })
        
        # Determine primary specialty from taxonomies
        primary_specialty = None
        if taxonomies:
            primary_specialty = taxonomies[0].get('description', '')
        
        return {
            "npi": provider_data.get('number', npi),
            "name": {
                "first": basic_info.get('first_name', ''),
                "last": basic_info.get('last_name', ''),
                "organization": basic_info.get('organization_name', '')
            },
            "credentials": basic_info.get('credential', ''),
            "gender": basic_info.get('gender', ''),
            "enumeration_date": basic_info.get('enumeration_date', ''),
            "certification_date": basic_info.get('certification_date', ''),
            "practice_location": {
                "address": practice_address.get('address_1', ''),
                "city": practice_address.get('city', ''),
                "state": practice_address.get('state', ''),
                "postal_code": practice_address.get('postal_code', ''),
                "country": practice_address.get('country_code', 'US')
            },
            "specialty": primary_specialty,
            "taxonomies": taxonomies
        }
