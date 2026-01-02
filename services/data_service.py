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

from models import ProviderProfile, ProviderName, ProviderLocation, UtilizationData, ExclusionData, ProviderTaxonomy, LegalInformation
from .cms_service import CMSDataService
from .oig_service import OIGDataService
from .nppes_service import NPPESDataService
from .web_search_service import WebSearchService
from .legal_parser_service import LegalParserService


class DataService:
    """Unified service for collecting provider data from all sources."""
    
    def __init__(self):
        self.cms_service = CMSDataService()
        self.oig_service = OIGDataService()
        self.nppes_service = NPPESDataService()
        self.web_search_service = WebSearchService()
        self.legal_parser = LegalParserService()
    
    async def collect_all_sources(self, npi: str, provider_name: Optional[str] = None, specialty: Optional[str] = None, location: Optional[str] = None) -> Dict:
        """Collect data from all sources in parallel."""
        logger.info(f"Collecting data for NPI {npi} from all sources...")
        
        # First, collect NPPES data to get provider name if not provided
        nppes_data = await self.nppes_service.get_provider_details(npi)
        
        # Extract provider name if not provided
        if not provider_name and not isinstance(nppes_data, Exception):
            name_data = nppes_data.get('name', {})
            if name_data.get('organization'):
                provider_name = name_data['organization']
            else:
                first = name_data.get('first', '')
                last = name_data.get('last', '')
                provider_name = f"{first} {last}".strip() if first or last else None
        
        # Extract specialty and location if not provided
        if not specialty and not isinstance(nppes_data, Exception):
            specialty = nppes_data.get('specialty')
        
        if not location and not isinstance(nppes_data, Exception):
            loc_data = nppes_data.get('practice_location', {})
            location = loc_data.get('state')
        
        # Now collect CMS, OIG, and web search in parallel
        tasks = [
            self.cms_service.get_provider_utilization(npi),
            self.oig_service.check_provider_exclusion(npi),
        ]
        
        # Add web search task if we have provider name
        if provider_name:
            tasks.append(
                self.web_search_service.search_provider_legal_info(
                    provider_name,
                    npi,
                    specialty,
                    location
                )
            )
        else:
            # Return empty web search result if no name
            async def empty_web_search():
                return {"legal_results": [], "searches_performed": 0}
            tasks.append(empty_web_search())
        
        cms_data, oig_data, web_search_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle individual source failures
        results = {
            'cms': cms_data if not isinstance(cms_data, Exception) else {"error": str(cms_data)},
            'oig': oig_data if not isinstance(oig_data, Exception) else {"error": str(oig_data)},
            'nppes': nppes_data if not isinstance(nppes_data, Exception) else {"error": str(nppes_data)},
            'web_search': web_search_data if not isinstance(web_search_data, Exception) else {"error": str(web_search_data), "legal_results": []}
        }
        
        # Calculate data quality score
        results['data_quality'] = self._assess_data_quality(results)
        
        logger.info(f"Data collection complete. Quality score: {results['data_quality']:.2f}")
        
        return results
    
    def _assess_data_quality(self, results: Dict) -> float:
        """Assess overall data quality score (0.0-1.0)."""
        quality_score = 0.0
        
        # CMS: 0.3 weight (optional)
        if 'error' not in results.get('cms', {}):
            quality_score += 0.3
        elif results.get('cms', {}).get('error', '').startswith('No CMS data'):
            quality_score += 0.15  # Partial credit for "no data" vs connection error
        
        # OIG: 0.3 weight (important)
        if 'error' not in results.get('oig', {}):
            quality_score += 0.3
        
        # NPPES: 0.3 weight (important for name)
        if 'error' not in results.get('nppes', {}):
            quality_score += 0.3
        
        # Web Search: 0.1 weight (optional, nice to have)
        web_search = results.get('web_search', {})
        if 'error' not in web_search and web_search.get('searches_performed', 0) > 0:
            quality_score += 0.1
        
        return quality_score
    
    def fuse_data_sources(self, cms_data: Dict, oig_data: Dict, nppes_data: Dict, web_search_data: Optional[Dict] = None) -> ProviderProfile:
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
        
        # Parse legal information from web search results
        legal_information = []
        if web_search_data and 'error' not in web_search_data:
            search_results = web_search_data.get('legal_results', [])
            if search_results:
                legal_information = self.legal_parser.parse_legal_information(
                    search_results,
                    provider_name.full_name,
                    npi,
                    nppes_data.get('specialty'),
                    practice_location.state
                )
        
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
            legal_information=legal_information,
            data_sources={
                'cms': 'error' not in cms_data,
                'oig': 'error' not in oig_data,
                'nppes': 'error' not in nppes_data,
                'web_search': web_search_data is not None and 'error' not in web_search_data and web_search_data.get('searches_performed', 0) > 0
            }
        )
        
        return profile
    
    async def close(self):
        """Close all service connections."""
        await self.cms_service.close()
        await self.nppes_service.close()
        await self.web_search_service.close()