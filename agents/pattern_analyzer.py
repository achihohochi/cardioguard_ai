"""
Pattern Analyzer Agent
Fraud pattern detection and statistical analysis.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ProviderProfile, RiskAnalysis, FraudEvidence
from .base_agent import BaseAgent


class PatternAnalyzer(BaseAgent):
    """Agent responsible for detecting fraud patterns and calculating risk scores."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.anomaly_threshold = 2.5  # Z-score threshold for anomalies
    
    def analyze_fraud_patterns(self, provider: ProviderProfile) -> RiskAnalysis:
        """Main analysis orchestration for fraud pattern detection."""
        self.log_activity("pattern_analysis_started", {"npi": provider.npi})
        
        try:
            # Statistical anomaly detection
            anomalies = self.calculate_statistical_anomalies(provider)
            
            # Temporal pattern analysis (if temporal data available)
            temporal_patterns = self.detect_temporal_patterns(provider)
            
            # Geographic pattern analysis
            geographic_patterns = self.analyze_geographic_patterns(provider)
            
            # Compile evidence
            evidence = self._compile_evidence(provider, anomalies, temporal_patterns, geographic_patterns)
            
            # Calculate risk score
            risk_score = self.calculate_risk_score(anomalies, evidence, provider)
            
            # Determine priority level
            priority_level = self._determine_priority(risk_score)
            
            # Create risk analysis
            risk_analysis = RiskAnalysis(
                provider_npi=provider.npi,
                risk_score=risk_score,
                priority_level=priority_level,
                anomalies=anomalies,
                evidence=evidence,
                temporal_patterns=temporal_patterns,
                geographic_patterns=geographic_patterns
            )
            
            self.log_activity("pattern_analysis_completed", {
                "npi": provider.npi,
                "risk_score": risk_score,
                "priority": priority_level,
                "evidence_count": len(evidence)
            })
            
            return risk_analysis
            
        except Exception as e:
            error_result = self.handle_error(e, f"analyzing patterns for NPI {provider.npi}")
            raise Exception(f"Pattern Analyzer failed: {error_result['error_message']}")
    
    def calculate_statistical_anomalies(self, provider: ProviderProfile, peer_baseline: Optional[Dict] = None) -> Dict[str, Any]:
        """Calculate statistical anomalies vs peer baseline."""
        anomalies = {}
        utilization = provider.utilization_data
        
        # Default peer baseline if not provided (simplified for MVP)
        if peer_baseline is None:
            peer_baseline = self._get_default_baseline()
        
        # Analyze key metrics
        metrics = {
            'total_services': utilization.total_services,
            'unique_beneficiaries': utilization.unique_beneficiaries,
            'services_per_beneficiary': utilization.services_per_beneficiary,
            'total_charges': utilization.total_charges,
            'charge_to_payment_ratio': utilization.charge_to_payment_ratio
        }
        
        for metric_name, metric_value in metrics.items():
            if metric_value == 0:
                continue
            
            baseline = peer_baseline.get(metric_name, {})
            mean = baseline.get('mean', 0)
            std = baseline.get('std', 1)
            
            if std > 0:
                z_score = (metric_value - mean) / std
                
                if abs(z_score) > self.anomaly_threshold:
                    anomalies[metric_name] = {
                        'value': metric_value,
                        'mean': mean,
                        'std': std,
                        'z_score': z_score,
                        'is_anomaly': True,
                        'direction': 'high' if z_score > 0 else 'low'
                    }
        
        return anomalies
    
    def _get_default_baseline(self) -> Dict[str, Dict[str, float]]:
        """Get default peer baseline (simplified for MVP)."""
        # These are placeholder values - in production, would query CMS for actual peer data
        return {
            'total_services': {'mean': 1000, 'std': 200},
            'unique_beneficiaries': {'mean': 300, 'std': 50},
            'services_per_beneficiary': {'mean': 3.3, 'std': 1.0},
            'total_charges': {'mean': 500000, 'std': 100000},
            'charge_to_payment_ratio': {'mean': 1.2, 'std': 0.3}
        }
    
    def detect_temporal_patterns(self, provider: ProviderProfile) -> Dict[str, Any]:
        """Detect temporal billing patterns (end-of-month clustering, spikes)."""
        # Simplified temporal analysis - in production would analyze time-series data
        patterns = {
            'end_of_month_clustering': False,
            'volume_spikes': False,
            'temporal_anomalies': []
        }
        
        # Check if utilization suggests temporal anomalies
        utilization = provider.utilization_data
        
        # High services per beneficiary might indicate temporal clustering
        if utilization.services_per_beneficiary > 10:
            patterns['end_of_month_clustering'] = True
            patterns['temporal_anomalies'].append(
                f"High services per beneficiary ({utilization.services_per_beneficiary:.1f}) "
                "may indicate end-of-month billing clustering"
            )
        
        return patterns
    
    def analyze_geographic_patterns(self, provider: ProviderProfile) -> Dict[str, Any]:
        """Analyze geographic patterns and service area concentration."""
        patterns = {
            'service_area': provider.practice_location.state or 'Unknown',
            'geographic_anomalies': []
        }
        
        # Check if provider has practice location
        if not provider.practice_location.state:
            patterns['geographic_anomalies'].append("Missing practice location information")
        
        # Additional geographic analysis could be added here
        # (e.g., comparing service area to patient distribution)
        
        return patterns
    
    def calculate_risk_score(self, anomalies: Dict[str, Any], evidence: List[FraudEvidence], provider: ProviderProfile) -> int:
        """Calculate composite risk score (0-100)."""
        base_score = 0
        
        # Exclusion status (high weight)
        if provider.exclusion_data.excluded:
            base_score += 50
        
        # Statistical anomalies (weighted by severity)
        anomaly_scores = []
        for metric_name, anomaly_data in anomalies.items():
            z_score = abs(anomaly_data.get('z_score', 0))
            if z_score > self.anomaly_threshold:
                # Score increases with z-score magnitude
                score = min(30, (z_score - self.anomaly_threshold) * 10)
                anomaly_scores.append(score)
        
        if anomaly_scores:
            base_score += max(anomaly_scores)  # Use highest anomaly score
        
        # Evidence-based scoring
        high_severity_evidence = sum(1 for e in evidence if e.severity == 'high')
        medium_severity_evidence = sum(1 for e in evidence if e.severity == 'medium')
        
        base_score += high_severity_evidence * 10
        base_score += medium_severity_evidence * 5
        
        # Data quality penalty
        if not all(provider.data_sources.values()):
            base_score += 5  # Small penalty for incomplete data
        
        # Cap at 100
        risk_score = min(100, int(base_score))
        
        return risk_score
    
    def _determine_priority(self, risk_score: int) -> str:
        """Determine priority level based on risk score."""
        if risk_score < 30:
            return "low"
        elif risk_score < 70:
            return "medium"
        else:
            return "high"
    
    def _compile_evidence(self, provider: ProviderProfile, anomalies: Dict, 
                         temporal_patterns: Dict, geographic_patterns: Dict) -> List[FraudEvidence]:
        """Compile fraud evidence from all analysis sources."""
        evidence = []
        
        # Exclusion evidence
        if provider.exclusion_data.excluded:
            evidence.append(FraudEvidence(
                evidence_type="oig_exclusion",
                description=f"Provider is excluded from Medicare/Medicaid: {provider.exclusion_data.exclusion_description}",
                statistical_significance=1.0,
                data_source="OIG",
                regulatory_citation="42 CFR §1001.101",
                severity="high"
            ))
        
        # Statistical anomaly evidence
        for metric_name, anomaly_data in anomalies.items():
            z_score = anomaly_data.get('z_score', 0)
            direction = anomaly_data.get('direction', 'high')
            value = anomaly_data.get('value', 0)
            
            severity = "high" if abs(z_score) > 3.0 else "medium"
            
            evidence.append(FraudEvidence(
                evidence_type=f"billing_anomaly_{metric_name}",
                description=f"{metric_name.replace('_', ' ').title()} is {direction} "
                           f"(Z-score: {z_score:.2f}, Value: {value})",
                statistical_significance=min(1.0, abs(z_score) / 5.0),
                data_source="CMS",
                regulatory_citation="42 CFR §424.516",
                severity=severity
            ))
        
        # Temporal pattern evidence
        if temporal_patterns.get('end_of_month_clustering'):
            evidence.append(FraudEvidence(
                evidence_type="temporal_clustering",
                description="Potential end-of-month billing clustering detected",
                statistical_significance=0.7,
                data_source="CMS",
                regulatory_citation="42 CFR §424.516",
                severity="medium"
            ))
        
        # Geographic anomaly evidence
        if geographic_patterns.get('geographic_anomalies'):
            for anomaly in geographic_patterns['geographic_anomalies']:
                evidence.append(FraudEvidence(
                    evidence_type="geographic_anomaly",
                    description=anomaly,
                    statistical_significance=0.5,
                    data_source="NPPES",
                    severity="low"
                ))
        
        return evidence
