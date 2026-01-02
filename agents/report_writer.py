"""
Report Writer Agent
Investigation report generation using Claude Haiku.
"""

from typing import Dict, Any, List
from loguru import logger

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic client not available. Install with: pip install anthropic")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import InvestigationReport, RiskAnalysis, FraudEvidence, ProviderProfile
from .base_agent import BaseAgent
from config import ANTHROPIC_API_KEY, PREFERRED_MODEL, MAX_TOKENS_PER_REQUEST


class ReportWriter(BaseAgent):
    """Agent responsible for generating investigation reports."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.client = None
        
        if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
            try:
                self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
    
    async def generate_investigation_report(
        self, 
        risk_analysis: RiskAnalysis,
        provider_profile: ProviderProfile
    ) -> InvestigationReport:
        """Generate complete investigation report."""
        self.log_activity("report_generation_started", {"npi": risk_analysis.provider_npi})
        
        try:
            # Generate executive summary
            executive_summary = await self.create_executive_summary(
                risk_analysis.risk_score,
                risk_analysis.evidence,
                provider_profile
            )
            
            # Generate recommendations
            recommendations = await self.create_recommendations(
                risk_analysis.risk_score,
                risk_analysis.evidence,
                risk_analysis.priority_level
            )
            
            # Extract regulatory citations
            regulatory_citations = self._extract_regulatory_citations(risk_analysis.evidence)
            
            # Create investigation report
            report = InvestigationReport(
                provider_npi=risk_analysis.provider_npi,
                provider_name=provider_profile.name.full_name,
                risk_score=risk_analysis.risk_score,
                priority_level=risk_analysis.priority_level,
                executive_summary=executive_summary,
                evidence_summary=risk_analysis.evidence,
                recommendations=recommendations,
                regulatory_citations=regulatory_citations
            )
            
            self.log_activity("report_generation_completed", {
                "npi": risk_analysis.provider_npi,
                "recommendations_count": len(recommendations)
            })
            
            return report
            
        except Exception as e:
            error_result = self.handle_error(e, f"generating report for NPI {risk_analysis.provider_npi}")
            raise Exception(f"Report Writer failed: {error_result['error_message']}")
    
    async def create_executive_summary(
        self,
        risk_score: int,
        evidence: List[FraudEvidence],
        provider_profile: ProviderProfile
    ) -> str:
        """Create executive summary using Claude Haiku."""
        if not self.client:
            # Fallback to template-based summary if Claude unavailable
            return self._create_template_summary(risk_score, evidence, provider_profile)
        
        try:
            # Prepare evidence summary
            evidence_summary = "\n".join([
                f"- {e.description} (Severity: {e.severity})"
                for e in evidence[:5]  # Limit to top 5 for token efficiency
            ])
            
            prompt = f"""Generate a concise executive summary (2-3 paragraphs) for a healthcare fraud investigation report.

Provider: {provider_profile.name.full_name} (NPI: {provider_profile.npi})
Risk Score: {risk_score}/100
Priority Level: {"High" if risk_score >= 70 else "Medium" if risk_score >= 30 else "Low"}

Key Findings:
{evidence_summary}

Requirements:
- Professional tone suitable for compliance team
- Highlight most critical findings
- Include risk assessment
- Keep under 200 words
- No markdown formatting, plain text only"""

            response = self.client.messages.create(
                model=PREFERRED_MODEL,
                max_tokens=MAX_TOKENS_PER_REQUEST,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            summary = response.content[0].text.strip()
            return summary
            
        except Exception as e:
            logger.warning(f"Claude API call failed, using template: {e}")
            return self._create_template_summary(risk_score, evidence, provider_profile)
    
    def _create_template_summary(self, risk_score: int, evidence: List[FraudEvidence], 
                               provider_profile: ProviderProfile) -> str:
        """Create template-based executive summary as fallback."""
        priority = "High" if risk_score >= 70 else "Medium" if risk_score >= 30 else "Low"
        
        summary = f"""This investigation report analyzes the fraud risk profile of provider {provider_profile.name.full_name} (NPI: {provider_profile.npi}).

The analysis indicates a {priority.lower()} risk level with a risk score of {risk_score}/100. """
        
        if evidence:
            high_severity = [e for e in evidence if e.severity == 'high']
            if high_severity:
                summary += f"Key findings include {len(high_severity)} high-severity indicators, including {high_severity[0].description}. "
        
        summary += f"""The provider's billing patterns, regulatory status, and utilization metrics have been evaluated against peer baselines and regulatory standards.

Based on this analysis, {'immediate investigation is recommended' if risk_score >= 70 else 'further monitoring may be warranted' if risk_score >= 30 else 'no immediate concerns identified'}."""
        
        return summary
    
    async def create_recommendations(
        self,
        risk_score: int,
        evidence: List[FraudEvidence],
        priority_level: str
    ) -> List[str]:
        """Create actionable investigation recommendations."""
        recommendations = []
        
        # Base recommendations on risk score
        if risk_score >= 70:
            recommendations.append("Prioritize for immediate investigation due to high risk score")
            recommendations.append("Review detailed billing records for the past 12 months")
            recommendations.append("Conduct provider interview to address identified anomalies")
        elif risk_score >= 30:
            recommendations.append("Schedule routine review within 30 days")
            recommendations.append("Monitor billing patterns for next quarter")
            recommendations.append("Request clarification on identified anomalies")
        else:
            recommendations.append("Continue routine monitoring")
            recommendations.append("No immediate action required")
        
        # Evidence-specific recommendations
        high_severity_evidence = [e for e in evidence if e.severity == 'high']
        if high_severity_evidence:
            recommendations.append(f"Address {len(high_severity_evidence)} high-severity findings")
        
        exclusion_evidence = [e for e in evidence if e.evidence_type == 'oig_exclusion']
        if exclusion_evidence:
            recommendations.append("Verify exclusion status and compliance requirements")
        
        anomaly_evidence = [e for e in evidence if 'billing_anomaly' in e.evidence_type]
        if anomaly_evidence:
            recommendations.append("Request detailed billing documentation for anomaly review")
        
        return recommendations
    
    def _extract_regulatory_citations(self, evidence: List[FraudEvidence]) -> List[str]:
        """Extract unique regulatory citations from evidence."""
        citations = set()
        
        for e in evidence:
            if e.regulatory_citation:
                citations.add(e.regulatory_citation)
        
        # Add standard citations
        citations.add("42 CFR §424.516 - Provider enrollment and screening")
        citations.add("42 CFR §1001.101 - OIG exclusion authorities")
        
        return sorted(list(citations))
