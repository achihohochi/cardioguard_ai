"""
Fraud Investigation Workflow
Orchestrates all agents in the fraud detection pipeline.
"""

import asyncio
from typing import Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from models import InvestigationReport, ProviderProfile, RiskAnalysis
from agents.research_agent import ResearchAgent
from agents.pattern_analyzer import PatternAnalyzer
from agents.report_writer import ReportWriter
from agents.quality_checker import QualityChecker


class FraudInvestigationWorkflow:
    """Main workflow coordinator for fraud investigation."""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.pattern_analyzer = PatternAnalyzer()
        self.report_writer = ReportWriter()
        self.quality_checker = QualityChecker()
    
    async def run_investigation(self, npi: str) -> InvestigationReport:
        """Run complete fraud investigation workflow."""
        logger.info(f"Starting fraud investigation for NPI {npi}")
        
        try:
            # Step 1: Research Agent - Data Collection
            logger.info("Step 1: Collecting provider intelligence...")
            provider_profile = await self.research_agent.collect_provider_intelligence(npi)
            
            # Step 2: Pattern Analyzer - Fraud Detection
            logger.info("Step 2: Analyzing fraud patterns...")
            risk_analysis = self.pattern_analyzer.analyze_fraud_patterns(provider_profile)
            
            # Step 3: Report Writer - Report Generation
            logger.info("Step 3: Generating investigation report...")
            draft_report = await self.report_writer.generate_investigation_report(
                risk_analysis,
                provider_profile
            )
            
            # Step 4: Quality Checker - Validation
            logger.info("Step 4: Validating report quality...")
            is_valid, validation_results = self.quality_checker.validate_report_quality(draft_report)
            
            if not is_valid:
                logger.warning(f"Report quality below threshold: {validation_results['quality_score']:.2f}")
                # For MVP, we'll still return the report but log the warning
                # In production, might want to retry or flag for manual review
            
            logger.info(f"Investigation complete. Risk score: {draft_report.risk_score}/100")
            
            return draft_report
            
        except Exception as e:
            logger.error(f"Workflow failed for NPI {npi}: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close all agent connections."""
        await self.research_agent.close()


# Convenience function for async execution
async def analyze_provider_fraud_risk(npi: str) -> InvestigationReport:
    """Analyze provider fraud risk and return investigation report."""
    workflow = FraudInvestigationWorkflow()
    try:
        report = await workflow.run_investigation(npi)
        return report
    finally:
        await workflow.close()


# Synchronous wrapper for Streamlit
def analyze_provider_sync(npi: str) -> InvestigationReport:
    """Synchronous wrapper for Streamlit compatibility."""
    return asyncio.run(analyze_provider_fraud_risk(npi))
