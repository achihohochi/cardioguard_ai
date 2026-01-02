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

from config import CMS_API_BASE_URL, CMS_DATASET_ID, CMS_CACHE_DURATION, CACHE_DIR


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
            
            # CMS Open Data API v1 endpoint
            # Base URL: https://data.cms.gov/data-api/v1/dataset/
            # Dataset ID: mj5m-pzi6 (provider summary data)
            url = f"{self.base_url}{CMS_DATASET_ID}/data"
            
            # CMS API v1 uses filter[npi] format (no quotes around NPI value)
            params = {
                f"filter[npi]": npi,
                "limit": 1000
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
                    # CMS is optional - log warning instead of error
                    # System works with just OIG + NPPES for excluded providers
                    warning_msg = f"CMS API returned status {response.status} - CMS data unavailable (optional)"
                    logger.warning(warning_msg)
                    return {
                        "error": warning_msg,
                        "total_services": 0,
                        "unique_beneficiaries": 0,
                        "total_charges": 0.0,
                        "total_payments": 0.0,
                        "provider_type": "Unknown",
                        "medicare_participation": "Unknown",
                        "npi": npi
                    }
                    
        except asyncio.TimeoutError:
            # CMS is optional - log warning instead of error
            warning_msg = "CMS API timeout - CMS data unavailable (optional, system continues with OIG + NPPES)"
            logger.warning(warning_msg)
            return {
                "error": warning_msg,
                "total_services": 0,
                "unique_beneficiaries": 0,
                "total_charges": 0.0,
                "total_payments": 0.0,
                "provider_type": "Unknown",
                "medicare_participation": "Unknown",
                "npi": npi
            }
        except Exception as e:
            # CMS is optional - log warning instead of error
            warning_msg = f"CMS connection failed: {str(e)} - CMS data unavailable (optional, system continues with OIG + NPPES)"
            logger.warning(warning_msg)
            return {
                "error": warning_msg,
                "total_services": 0,
                "unique_beneficiaries": 0,
                "total_charges": 0.0,
                "total_payments": 0.0,
                "provider_type": "Unknown",
                "medicare_participation": "Unknown",
                "npi": npi
            }
    
    def _process_cms_response(self, raw_data: Dict, npi: str) -> Dict:
        """Process CMS API response into standardized format."""
        # Handle CMS Open Data API v1 response format
        # Response can be: list of records, or dict with 'data' key, or single record dict
        
        provider_data = {}
        
        if isinstance(raw_data, list):
            # API returns list of records - aggregate if multiple
            if len(raw_data) > 0:
                # Aggregate multiple records for same NPI
                total_services = sum(int(r.get('line_srvc_cnt', r.get('total_services', 0))) for r in raw_data)
                total_beneficiaries = sum(int(r.get('bene_unique_cnt', r.get('unique_beneficiaries', 0))) for r in raw_data)
                total_charges = sum(float(r.get('total_sbmtd_chrg', r.get('total_charges', 0.0))) for r in raw_data)
                total_payments = sum(float(r.get('total_medicare_payment_amt', r.get('total_payments', 0.0))) for r in raw_data)
                
                # Use first record for metadata
                provider_data = raw_data[0].copy()
                provider_data['line_srvc_cnt'] = total_services
                provider_data['bene_unique_cnt'] = total_beneficiaries
                provider_data['total_sbmtd_chrg'] = total_charges
                provider_data['total_medicare_payment_amt'] = total_payments
            else:
                return {"error": f"No CMS data found for NPI {npi}"}
        elif isinstance(raw_data, dict):
            if 'data' in raw_data:
                # Nested data structure
                data_list = raw_data['data']
                if isinstance(data_list, list) and len(data_list) > 0:
                    provider_data = data_list[0]
                else:
                    return {"error": f"No CMS data found for NPI {npi}"}
            else:
                # Single record dict
                provider_data = raw_data
        else:
            return {"error": f"Unexpected CMS API response format for NPI {npi}"}
        
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
