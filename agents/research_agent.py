"""
Research Agent
Multi-source healthcare data collection and provider profiling.
"""

from typing import Dict, Any
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ProviderProfile
from .base_agent import BaseAgent
from services.data_service import DataService


class ResearchAgent(BaseAgent):
    """Agent responsible for collecting provider intelligence from multiple sources."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.data_service = DataService()
    
    async def collect_provider_intelligence(self, npi: str) -> ProviderProfile:
        """Collect comprehensive provider intelligence from all sources."""
        self.log_activity("collect_intelligence_started", {"npi": npi})
        
        try:
            # Validate NPI format
            if not npi or not npi.isdigit() or len(npi) != 10:
                raise ValueError(f"Invalid NPI format: {npi}. Must be exactly 10 digits.")
            
            # Collect data from all sources in parallel
            all_data = await self.data_service.collect_all_sources(npi)
            
            # Extract individual source data
            cms_data = all_data.get('cms', {})
            oig_data = all_data.get('oig', {})
            nppes_data = all_data.get('nppes', {})
            
            # Fuse data into unified provider profile
            provider_profile = self.data_service.fuse_data_sources(
                cms_data, oig_data, nppes_data
            )
            
            # Identify initial risk factors
            risk_factors = self._identify_risk_factors(provider_profile)
            provider_profile.risk_factors = risk_factors
            
            self.log_activity("collect_intelligence_completed", {
                "npi": npi,
                "data_sources": provider_profile.data_sources,
                "risk_factors_count": len(risk_factors)
            })
            
            return provider_profile
            
        except Exception as e:
            error_result = self.handle_error(e, f"collecting intelligence for NPI {npi}")
            raise Exception(f"Research Agent failed: {error_result['error_message']}")
    
    def _identify_risk_factors(self, profile: ProviderProfile) -> list[str]:
        """Identify initial risk factors from collected data."""
        risk_factors = []
        
        # Check exclusion status
        if profile.exclusion_data.excluded:
            risk_factors.append(f"OIG Exclusion: {profile.exclusion_data.exclusion_description}")
        
        # Check utilization anomalies (preliminary)
        utilization = profile.utilization_data
        if utilization.total_services > 0 and utilization.unique_beneficiaries > 0:
            services_per_beneficiary = utilization.services_per_beneficiary
            if services_per_beneficiary > 50:  # Threshold for high services per beneficiary
                risk_factors.append(f"High services per beneficiary: {services_per_beneficiary:.1f}")
        
        # Check charge-to-payment ratio
        if utilization.charge_to_payment_ratio > 2.0:  # High ratio may indicate upcoding
            risk_factors.append(f"High charge-to-payment ratio: {utilization.charge_to_payment_ratio:.2f}")
        
        # Check data quality
        if not all(profile.data_sources.values()):
            missing_sources = [k for k, v in profile.data_sources.items() if not v]
            risk_factors.append(f"Incomplete data: missing {', '.join(missing_sources)}")
        
        return risk_factors
    
    async def get_cms_utilization_data(self, npi: str) -> Dict[str, Any]:
        """Get CMS utilization data for provider."""
        return await self.data_service.cms_service.get_provider_utilization(npi)
    
    async def check_oig_exclusion_status(self, npi: str) -> Dict[str, Any]:
        """Check OIG exclusion status for provider."""
        return await self.data_service.oig_service.check_provider_exclusion(npi)
    
    async def get_provider_credentials(self, npi: str) -> Dict[str, Any]:
        """Get provider credentials from NPPES."""
        return await self.data_service.nppes_service.get_provider_details(npi)
    
    async def close(self):
        """Close data service connections."""
        await self.data_service.close()
