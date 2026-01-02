"""
CardioGuard_AI Data Models
Pydantic models for type safety and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ProviderLocation(BaseModel):
    """Provider practice location information."""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "US"


class ProviderName(BaseModel):
    """Provider name information."""
    first: Optional[str] = None
    last: Optional[str] = None
    organization: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get full provider name."""
        if self.organization:
            return self.organization
        parts = [p for p in [self.first, self.last] if p]
        return " ".join(parts) if parts else "Unknown"


class ProviderTaxonomy(BaseModel):
    """Provider taxonomy/specialty information."""
    code: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    state: Optional[str] = None


class UtilizationData(BaseModel):
    """Provider utilization and billing data."""
    total_services: int = 0
    unique_beneficiaries: int = 0
    total_charges: float = 0.0
    total_payments: float = 0.0
    provider_type: Optional[str] = None
    medicare_participation: Optional[str] = None
    
    @property
    def services_per_beneficiary(self) -> float:
        """Calculate services per beneficiary ratio."""
        if self.unique_beneficiaries == 0:
            return 0.0
        return self.total_services / self.unique_beneficiaries
    
    @property
    def charge_to_payment_ratio(self) -> float:
        """Calculate charge to payment ratio."""
        if self.total_payments == 0:
            return 0.0
        return self.total_charges / self.total_payments


class ExclusionData(BaseModel):
    """OIG exclusion information."""
    excluded: bool = False
    exclusion_type: Optional[str] = None
    exclusion_date: Optional[str] = None
    reinstatement_date: Optional[str] = None
    exclusion_description: Optional[str] = None
    state: Optional[str] = None


class LegalInformation(BaseModel):
    """Legal/court information from web search."""
    case_type: str = Field(..., description="Type of case: conviction, lawsuit, allegation, pending")
    status: str = Field(..., description="Status: convicted, pending, settled, dismissed")
    date: Optional[str] = Field(None, description="Date of case/conviction if available")
    description: str = Field(..., description="Description of the legal case")
    source_url: str = Field(..., description="URL of the source")
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score (0.0-1.0)"
    )
    verified: bool = Field(
        default=False,
        description="True if from official court/government source"
    )


class ProviderProfile(BaseModel):
    """Comprehensive provider profile combining all data sources."""
    npi: str = Field(..., description="National Provider Identifier")
    name: ProviderName = Field(default_factory=ProviderName)
    credentials: Optional[str] = None
    specialty: Optional[str] = None
    practice_location: ProviderLocation = Field(default_factory=ProviderLocation)
    utilization_data: UtilizationData = Field(default_factory=UtilizationData)
    exclusion_data: ExclusionData = Field(default_factory=ExclusionData)
    taxonomies: List[ProviderTaxonomy] = Field(default_factory=list)
    enumeration_date: Optional[str] = None
    certification_date: Optional[str] = None
    risk_factors: List[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    legal_information: List[LegalInformation] = Field(
        default_factory=list,
        description="Legal/court information from web search"
    )
    data_sources: Dict[str, bool] = Field(
        default_factory=lambda: {"cms": False, "oig": False, "nppes": False, "web_search": False}
    )
    collected_at: datetime = Field(default_factory=datetime.now)
    
    @validator("npi")
    def validate_npi(cls, v):
        """Validate NPI format (10 digits)."""
        if not v or not v.isdigit() or len(v) != 10:
            raise ValueError("NPI must be exactly 10 digits")
        return v


class FraudEvidence(BaseModel):
    """Individual piece of fraud evidence."""
    evidence_type: str = Field(..., description="Type of evidence (e.g., billing_anomaly)")
    description: str = Field(..., description="Description of the evidence")
    statistical_significance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Statistical significance score (0-1)"
    )
    data_source: str = Field(..., description="Source of the evidence (CMS, OIG, etc.)")
    regulatory_citation: Optional[str] = Field(
        None,
        description="Relevant regulatory citation"
    )
    severity: str = Field(
        default="medium",
        description="Severity level: low, medium, high"
    )
    
    @validator("severity")
    def validate_severity(cls, v):
        """Validate severity level."""
        if v not in ["low", "medium", "high"]:
            raise ValueError("Severity must be low, medium, or high")
        return v


class RiskAnalysis(BaseModel):
    """Fraud risk analysis results."""
    provider_npi: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    priority_level: str = Field(..., description="Priority: low, medium, high")
    anomalies: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[FraudEvidence] = Field(default_factory=list)
    peer_comparison: Optional[Dict[str, Any]] = None
    temporal_patterns: Optional[Dict[str, Any]] = None
    geographic_patterns: Optional[Dict[str, Any]] = None
    analyzed_at: datetime = Field(default_factory=datetime.now)
    
    @validator("priority_level")
    def validate_priority(cls, v, values):
        """Set priority based on risk score."""
        if "risk_score" in values:
            score = values["risk_score"]
            if score < 30:
                return "low"
            elif score < 70:
                return "medium"
            else:
                return "high"
        return v


class InvestigationReport(BaseModel):
    """Complete investigation report."""
    provider_npi: str
    provider_name: str
    risk_score: int = Field(..., ge=0, le=100)
    priority_level: str
    executive_summary: str
    evidence_summary: List[FraudEvidence] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    regulatory_citations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)
    report_version: str = "1.0"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
