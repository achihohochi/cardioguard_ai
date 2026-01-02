"""
CMS Open Data Service
Integration with CMS provider utilization data API.
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

from config import CMS_API_BASE_URL, CMS_CACHE_DURATION, CACHE_DIR


class CMSDataService:
    """Service for accessing CMS Open Data API."""
    
    def __init__(self):
        self.base_url = CMS_API_BASE_URL
        self.cache_dir = CACHE_DIR / "cms"
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
        return self.cache_dir / f"cms_{npi}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid."""
        if not cache_path.exists():
            return False
        
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        return cache_age.total_seconds() < CMS_CACHE_DURATION
    
    async def get_provider_utilization(self, npi: str) -> Dict:
        """Get provider utilization data from CMS."""
        cache_path = self._get_cache_path(npi)
        
        # Check cache first
        if self._is_cache_valid(cache_path):
            logger.info(f"Using cached CMS data for NPI {npi}")
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        
        # Fetch from API
        try:
            session = await self._get_session()
            
            # Note: CMS API endpoint structure may vary
            # This is a placeholder - actual endpoint needs to be determined
            # Based on CMS Open Data portal structure
            url = f"{self.base_url}datastore/rest/filter"
            
            # CMS uses Socrata API format
            params = {
                "npi": npi,
                "$limit": 1000
            }
            
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    processed_data = self._process_cms_response(data, npi)
                    
                    # Cache the result
                    try:
                        with open(cache_path, 'w') as f:
                            json.dump(processed_data, f)
                    except Exception as e:
                        logger.warning(f"Failed to cache CMS data: {e}")
                    
                    return processed_data
                else:
                    error_msg = f"CMS API error: {response.status}"
                    logger.error(error_msg)
                    return {"error": error_msg}
                    
        except asyncio.TimeoutError:
            error_msg = "CMS API timeout"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"CMS connection failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _process_cms_response(self, raw_data: Dict, npi: str) -> Dict:
        """Process CMS API response into standardized format."""
        # Handle different CMS API response formats
        if isinstance(raw_data, list) and len(raw_data) > 0:
            provider_data = raw_data[0]
        elif isinstance(raw_data, dict) and 'data' in raw_data:
            provider_data = raw_data['data'][0] if raw_data['data'] else {}
        elif isinstance(raw_data, dict):
            provider_data = raw_data
        else:
            return {"error": f"No CMS data found for NPI {npi}"}
        
        # Extract key utilization metrics with fallbacks for different field names
        return {
            "total_services": int(provider_data.get('line_srvc_cnt', 
                                                    provider_data.get('total_services', 0))),
            "unique_beneficiaries": int(provider_data.get('bene_unique_cnt',
                                                          provider_data.get('unique_beneficiaries', 0))),
            "total_charges": float(provider_data.get('total_sbmtd_chrg',
                                                     provider_data.get('total_charges', 0.0))),
            "total_payments": float(provider_data.get('total_medicare_payment_amt',
                                                      provider_data.get('total_payments', 0.0))),
            "provider_type": provider_data.get('provider_type', 
                                              provider_data.get('entity_type', 'Unknown')),
            "medicare_participation": provider_data.get('medicare_participation_indicator',
                                                       provider_data.get('participation', 'Unknown')),
            "npi": npi
        }
    
    async def get_peer_baseline(self, specialty: str, state: str, limit: int = 50) -> Dict:
        """Get peer provider baseline statistics."""
        # This would query CMS for similar providers
        # Placeholder implementation
        logger.info(f"Getting peer baseline for specialty {specialty}, state {state}")
        return {
            "peer_count": 0,
            "baselines": {}
        }
