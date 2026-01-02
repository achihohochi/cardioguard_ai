"""
Quality Checker Agent
Report validation and quality assurance.
"""

from typing import Dict, Any, List
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import InvestigationReport
from .base_agent import BaseAgent


class QualityChecker(BaseAgent):
    """Agent responsible for validating report quality."""
    
    REQUIRED_SECTIONS = [
        'executive_summary',
        'evidence_summary',
        'recommendations',
        'regulatory_citations'
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_quality_score = 0.8  # Minimum quality score threshold
    
    def validate_report_quality(self, report: InvestigationReport) -> tuple[bool, Dict[str, Any]]:
        """Validate report quality and return (is_valid, validation_results)."""
        self.log_activity("quality_check_started", {"npi": report.provider_npi})
        
        validation_results = {
            'completeness': self.check_completeness(report),
            'evidence_accuracy': self.validate_evidence_accuracy(report.evidence_summary),
            'regulatory_compliance': self.verify_regulatory_compliance(report),
            'professional_standards': self.check_professional_standards(report)
        }
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(validation_results)
        validation_results['quality_score'] = quality_score
        validation_results['is_valid'] = quality_score >= self.min_quality_score
        
        self.log_activity("quality_check_completed", {
            "npi": report.provider_npi,
            "quality_score": quality_score,
            "is_valid": validation_results['is_valid']
        })
        
        return validation_results['is_valid'], validation_results
    
    def check_completeness(self, report: InvestigationReport) -> Dict[str, Any]:
        """Verify all required sections are present."""
        completeness = {
            'all_sections_present': True,
            'missing_sections': [],
            'section_details': {}
        }
        
        # Check executive summary
        if not report.executive_summary or len(report.executive_summary.strip()) < 50:
            completeness['all_sections_present'] = False
            completeness['missing_sections'].append('executive_summary')
        completeness['section_details']['executive_summary'] = {
            'present': bool(report.executive_summary),
            'length': len(report.executive_summary) if report.executive_summary else 0
        }
        
        # Check evidence summary
        if not report.evidence_summary or len(report.evidence_summary) == 0:
            completeness['all_sections_present'] = False
            completeness['missing_sections'].append('evidence_summary')
        completeness['section_details']['evidence_summary'] = {
            'present': len(report.evidence_summary) > 0,
            'count': len(report.evidence_summary)
        }
        
        # Check recommendations
        if not report.recommendations or len(report.recommendations) == 0:
            completeness['all_sections_present'] = False
            completeness['missing_sections'].append('recommendations')
        completeness['section_details']['recommendations'] = {
            'present': len(report.recommendations) > 0,
            'count': len(report.recommendations)
        }
        
        # Check regulatory citations
        if not report.regulatory_citations or len(report.regulatory_citations) == 0:
            completeness['all_sections_present'] = False
            completeness['missing_sections'].append('regulatory_citations')
        completeness['section_details']['regulatory_citations'] = {
            'present': len(report.regulatory_citations) > 0,
            'count': len(report.regulatory_citations)
        }
        
        return completeness
    
    def validate_evidence_accuracy(self, evidence: List) -> Dict[str, Any]:
        """Check evidence relevance and accuracy."""
        accuracy = {
            'all_evidence_valid': True,
            'issues': [],
            'evidence_count': len(evidence)
        }
        
        for i, ev in enumerate(evidence):
            # Check evidence has required fields
            if not ev.description or len(ev.description.strip()) < 10:
                accuracy['all_evidence_valid'] = False
                accuracy['issues'].append(f"Evidence {i+1}: Description too short or missing")
            
            if not ev.data_source:
                accuracy['all_evidence_valid'] = False
                accuracy['issues'].append(f"Evidence {i+1}: Missing data source")
            
            if ev.statistical_significance < 0 or ev.statistical_significance > 1:
                accuracy['all_evidence_valid'] = False
                accuracy['issues'].append(f"Evidence {i+1}: Invalid statistical significance")
        
        return accuracy
    
    def verify_regulatory_compliance(self, report: InvestigationReport) -> Dict[str, Any]:
        """Ensure proper regulatory citations."""
        compliance = {
            'has_citations': len(report.regulatory_citations) > 0,
            'citation_count': len(report.regulatory_citations),
            'standard_citations_present': False
        }
        
        # Check for standard citations
        citation_text = ' '.join(report.regulatory_citations).lower()
        if '42 cfr' in citation_text or 'cfr' in citation_text:
            compliance['standard_citations_present'] = True
        
        return compliance
    
    def check_professional_standards(self, report: InvestigationReport) -> Dict[str, Any]:
        """Check report meets professional standards."""
        standards = {
            'meets_standards': True,
            'issues': []
        }
        
        # Check executive summary length (should be substantial)
        if len(report.executive_summary) < 100:
            standards['meets_standards'] = False
            standards['issues'].append("Executive summary too brief")
        
        # Check recommendations are actionable
        if report.recommendations:
            vague_words = ['consider', 'maybe', 'possibly', 'perhaps']
            for rec in report.recommendations:
                if any(word in rec.lower() for word in vague_words):
                    standards['meets_standards'] = False
                    standards['issues'].append("Recommendations may be too vague")
        
        # Check risk score is reasonable
        if report.risk_score < 0 or report.risk_score > 100:
            standards['meets_standards'] = False
            standards['issues'].append("Invalid risk score")
        
        return standards
    
    def calculate_quality_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall quality score (0.0-1.0)."""
        scores = []
        
        # Completeness score (40% weight)
        completeness = validation_results['completeness']
        completeness_score = 1.0 if completeness['all_sections_present'] else 0.5
        scores.append(completeness_score * 0.4)
        
        # Evidence accuracy score (30% weight)
        evidence = validation_results['evidence_accuracy']
        evidence_score = 1.0 if evidence['all_evidence_valid'] else 0.7
        scores.append(evidence_score * 0.3)
        
        # Regulatory compliance score (20% weight)
        compliance = validation_results['regulatory_compliance']
        compliance_score = 1.0 if compliance['has_citations'] and compliance['standard_citations_present'] else 0.5
        scores.append(compliance_score * 0.2)
        
        # Professional standards score (10% weight)
        standards = validation_results['professional_standards']
        standards_score = 1.0 if standards['meets_standards'] else 0.7
        scores.append(standards_score * 0.1)
        
        return sum(scores)
