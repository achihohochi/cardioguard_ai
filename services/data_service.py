"""
Unified Data Service
Orchestrates data collection from all sources with parallel processing.
"""

import asyncio
from typing import Dict, Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ProviderProfile, ProviderName, ProviderLocation, UtilizationData, ExclusionData, ProviderTaxonomy
from .cms_service import CMSDataService
from .oig_service import OIGDataService
from .nppes_service import NPPESDataService


class DataService:
    """Unified service for collecting provider data from all sources."""
    
    def __init__(self):
        self.cms_service = CMSDataService()
        self.oig_service = OIGDataService()
        self.nppes_service = NPPESDataService()
    
    async def collect_all_sources(self, npi: str) -> Dict:
        """Collect data from all sources in parallel."""
        logger.info(f"Collecting data for NPI {npi} from all sources...")
        
        # Parallel data collection with error isolation
        tasks = [
            self.cms_service.get_provider_utilization(npi),
            self.oig_service.check_provider_exclusion(npi),
            self.nppes_service.get_provider_details(npi)
        ]
        
        cms_data, oig_data, nppes_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle individual source failures
        results = {
            'cms': cms_data if not isinstance(cms_data, Exception) else {"error": str(cms_data)},
            'oig': oig_data if not isinstance(oig_data, Exception) else {"error": str(oig_data)},
            'nppes': nppes_data if not isinstance(nppes_data, Exception) else {"error": str(nppes_data)}
        }
        
        # Calculate data quality score
        results['data_quality'] = self._assess_data_quality(results)
        
        logger.info(f"Data collection complete. Quality score: {results['data_quality']:.2f}")
        
        return results
    
    def _assess_data_quality(self, results: Dict) -> float:
        """Assess overall data quality score (0.0-1.0)."""
        quality_score = 0.0
        total_sources = 3
        
        if 'error' not in results.get('cms', {}):
            quality_score += 0.4
        elif results.get('cms', {}).get('error', '').startswith('No CMS data'):
            quality_score += 0.2  # Partial credit for "no data" vs connection error
        
        if 'error' not in results.get('oig', {}):
            quality_score += 0.3
        
        if 'error' not in results.get('nppes', {}):
            quality_score += 0.3
        
        return quality_score
    
    def fuse_data_sources(self, cms_data: Dict, oig_data: Dict, nppes_data: Dict) -> ProviderProfile:
        """Fuse data from all sources into unified ProviderProfile."""
        npi = nppes_data.get('npi') or cms_data.get('npi', '')
        
        if not npi:
            raise ValueError("NPI not found in any data source")
        
        # Build provider name
        name_data = nppes_data.get('name', {})
        provider_name = ProviderName(
            first=name_data.get('first', ''),
            last=name_data.get('last', ''),
            organization=name_data.get('organization', '')
        )
        
        # Build practice location
        location_data = nppes_data.get('practice_location', {})
        practice_location = ProviderLocation(
            address=location_data.get('address', ''),
            city=location_data.get('city', ''),
            state=location_data.get('state', ''),
            postal_code=location_data.get('postal_code', ''),
            country=location_data.get('country', 'US')
        )
        
        # Build utilization data
        utilization_data = UtilizationData(
            total_services=cms_data.get('total_services', 0),
            unique_beneficiaries=cms_data.get('unique_beneficiaries', 0),
            total_charges=cms_data.get('total_charges', 0.0),
            total_payments=cms_data.get('total_payments', 0.0),
            provider_type=cms_data.get('provider_type'),
            medicare_participation=cms_data.get('medicare_participation')
        )
        
        # Build exclusion data
        exclusion_data = ExclusionData(
            excluded=oig_data.get('excluded', False),
            exclusion_type=oig_data.get('exclusion_type'),
            exclusion_date=oig_data.get('exclusion_date'),
            reinstatement_date=oig_data.get('reinstatement_date'),
            exclusion_description=oig_data.get('exclusion_description'),
            state=oig_data.get('state')
        )
        
        # Build taxonomies
        taxonomies = []
        for tax_data in nppes_data.get('taxonomies', []):
            taxonomies.append(ProviderTaxonomy(
                code=tax_data.get('code'),
                description=tax_data.get('description'),
                license=tax_data.get('license'),
                state=tax_data.get('state')
            ))
        
        # Build provider profile
        profile = ProviderProfile(
            npi=npi,
            name=provider_name,
            credentials=nppes_data.get('credentials'),
            specialty=nppes_data.get('specialty'),
            practice_location=practice_location,
            utilization_data=utilization_data,
            exclusion_data=exclusion_data,
            taxonomies=taxonomies,
            enumeration_date=nppes_data.get('enumeration_date'),
            certification_date=nppes_data.get('certification_date'),
            data_sources={
                'cms': 'error' not in cms_data,
                'oig': 'error' not in oig_data,
                'nppes': 'error' not in nppes_data
            }
        )
        
        return profile
    
    async def close(self):
        """Close all service connections."""
        await self.cms_service.close()
        await self.nppes_service.close()
