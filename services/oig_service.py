"""
OIG Exclusion Database Service
Integration with HHS OIG exclusion database.
"""

import pandas as pd
import aiohttp
import asyncio
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OIG_EXCLUSIONS_URL, OIG_CACHE_DURATION, CACHE_DIR, OIG_API_TIMEOUT


# Exclusion type mappings
EXCLUSION_TYPES = {
    "1128a1": "Mandatory - Medicare/Medicaid conviction",
    "1128a2": "Mandatory - Patient abuse conviction",
    "1128a3": "Mandatory - Felony conviction",
    "1128b1": "Permissive - Misdemeanor conviction",
    "1128b2": "Permissive - License revocation",
    "1128b4": "Permissive - Default on health education loan"
}


class OIGDataService:
    """Service for accessing OIG exclusion database."""
    
    def __init__(self):
        self.exclusions_url = OIG_EXCLUSIONS_URL
        self.cache_file = CACHE_DIR / "oig_exclusions.csv"
        self.cache_dir = CACHE_DIR / "oig"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.exclusions_df: Optional[pd.DataFrame] = None
    
    def _is_cache_valid(self) -> bool:
        """Check if OIG exclusion cache is still valid."""
        if not self.cache_file.exists():
            return False
        
        cache_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        return cache_age.total_seconds() < OIG_CACHE_DURATION
    
    async def _download_exclusions_data(self) -> pd.DataFrame:
        """Download OIG exclusions CSV file."""
        logger.info("Downloading OIG exclusions database...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.exclusions_url, timeout=aiohttp.ClientTimeout(total=OIG_API_TIMEOUT)) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save to cache
                        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(self.cache_file, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f"OIG exclusions downloaded and cached: {len(content)} bytes")
                        
                        # Load into DataFrame
                        df = pd.read_csv(self.cache_file, low_memory=False)
                        logger.info(f"Loaded {len(df)} exclusion records")
                        return df
                    else:
                        raise Exception(f"Failed to download OIG data: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Failed to download OIG exclusions: {e}")
            # Try to use existing cache if available
            if self.cache_file.exists():
                logger.warning("Using stale OIG cache due to download failure")
                return pd.read_csv(self.cache_file, low_memory=False)
            raise
    
    async def _get_exclusions_data(self) -> pd.DataFrame:
        """Get OIG exclusions data with caching."""
        if self.exclusions_df is not None:
            return self.exclusions_df
        
        if self._is_cache_valid():
            logger.info("Using cached OIG exclusions data")
            self.exclusions_df = pd.read_csv(self.cache_file, low_memory=False)
            return self.exclusions_df
        
        # Download fresh data
        self.exclusions_df = await self._download_exclusions_data()
        return self.exclusions_df
    
    async def check_provider_exclusion(self, npi: str) -> Dict:
        """Check if provider is on OIG exclusion list."""
        try:
            exclusions_data = await self._get_exclusions_data()
            
            # Handle different column name variations
            npi_column = None
            for col in exclusions_data.columns:
                if col.upper() in ['NPI', 'NATIONAL_PROVIDER_IDENTIFIER']:
                    npi_column = col
                    break
            
            if npi_column is None:
                logger.warning("NPI column not found in OIG data")
                return {
                    "excluded": False,
                    "exclusion_status": "Data unavailable",
                    "error": "NPI column not found"
                }
            
            # Convert NPI to string for comparison
            exclusions_data[npi_column] = exclusions_data[npi_column].astype(str)
            
            # Search for provider NPI
            provider_exclusions = exclusions_data[exclusions_data[npi_column] == npi]
            
            if not provider_exclusions.empty:
                exclusion_record = provider_exclusions.iloc[0]
                return self._format_exclusion_data(exclusion_record)
            else:
                return {
                    "excluded": False,
                    "exclusion_status": "Not excluded",
                    "last_checked": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"OIG exclusion check failed: {e}")
            return {
                "excluded": False,
                "exclusion_status": "Check failed",
                "error": str(e)
            }
    
    def _format_exclusion_data(self, exclusion_record: pd.Series) -> Dict:
        """Format exclusion data for analysis."""
        # Handle different column name variations
        def get_value(key_variations, default=None):
            for key in key_variations:
                if key in exclusion_record.index:
                    val = exclusion_record[key]
                    if pd.notna(val):
                        return str(val)
            return default
        
        exclusion_type = get_value(['EXCLTYPE', 'EXCLUSION_TYPE', 'TYPE'], 'Unknown')
        exclusion_desc = EXCLUSION_TYPES.get(exclusion_type, 'Unknown exclusion type')
        
        first_name = get_value(['FIRSTNAME', 'FIRST_NAME', 'FNAME'], '')
        last_name = get_value(['LASTNAME', 'LAST_NAME', 'LNAME'], '')
        
        return {
            "excluded": True,
            "exclusion_type": exclusion_type,
            "exclusion_date": get_value(['EXCLDATE', 'EXCLUSION_DATE', 'DATE'], 'Unknown'),
            "reinstatement_date": get_value(['REINSTDATE', 'REINSTATEMENT_DATE'], None),
            "exclusion_description": exclusion_desc,
            "provider_name": f"{first_name} {last_name}".strip() or "Unknown",
            "state": get_value(['STATE', 'PROVIDER_STATE'], 'Unknown'),
            "last_checked": datetime.now().isoformat()
        }
