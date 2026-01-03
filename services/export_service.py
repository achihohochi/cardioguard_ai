"""
Export Service
PDF report generation using ReportLab.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available. Install with: pip install reportlab")

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import InvestigationReport


class ExportService:
    """Service for exporting investigation reports to PDF."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_pdf(self, report: InvestigationReport) -> Path:
        """Export investigation report to PDF."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"investigation_report_{report.provider_npi}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#1a1a1a',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Healthcare Fraud Investigation Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Provider Information
        story.append(Paragraph(f"<b>Provider NPI:</b> {report.provider_npi}", styles['Normal']))
        story.append(Paragraph(f"<b>Provider Name:</b> {report.provider_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Score:</b> {report.risk_score}/100", styles['Normal']))
        story.append(Paragraph(f"<b>Priority Level:</b> {report.priority_level.upper()}", styles['Normal']))
        story.append(Paragraph(f"<b>Report Date:</b> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(report.executive_summary, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Evidence Summary
        if report.evidence_summary:
            story.append(Paragraph("<b>Evidence Summary</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, evidence in enumerate(report.evidence_summary, 1):
                evidence_text = f"""
                <b>{i}. {evidence.evidence_type.replace('_', ' ').title()}</b><br/>
                {evidence.description}<br/>
                <i>Severity: {evidence.severity.upper()} | Source: {evidence.data_source}</i>
                """
                story.append(Paragraph(evidence_text, styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if report.recommendations:
            story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, recommendation in enumerate(report.recommendations, 1):
                story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Regulatory Citations
        if report.regulatory_citations:
            story.append(Paragraph("<b>Regulatory Citations</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for citation in report.regulatory_citations:
                story.append(Paragraph(f"• {citation}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Fraud Financial Data
        if report.fraud_financial_data:
            story.append(Paragraph("<b>Fraud Financial Impact</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            financial = report.fraud_financial_data
            
            if financial.estimated_fraud_amount:
                story.append(Paragraph(f"<b>Estimated Fraud Amount:</b> ${financial.estimated_fraud_amount:,.2f}", styles['Normal']))
            
            if financial.settlement_amount:
                story.append(Paragraph(f"<b>Settlement Amount:</b> ${financial.settlement_amount:,.2f}", styles['Normal']))
            
            if financial.restitution_amount:
                story.append(Paragraph(f"<b>Restitution Amount:</b> ${financial.restitution_amount:,.2f}", styles['Normal']))
            
            if financial.total_fraud_impact > 0:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>Total Fraud Impact:</b> ${financial.total_fraud_impact:,.2f}", styles['Heading3']))
            
            if financial.investigation_year:
                story.append(Paragraph(f"<b>Investigation Year:</b> {financial.investigation_year}", styles['Normal']))
            
            if financial.source:
                story.append(Paragraph(f"<b>Source:</b> {financial.source}", styles['Normal']))
            
            if financial.notes:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>Notes:</b> {financial.notes}", styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report exported: {filepath}")
        return filepath
    
    def get_report_path(self, npi: str) -> Optional[Path]:
        """Get the most recent report path for a provider NPI."""
        pattern = f"investigation_report_{npi}_*.pdf"
        reports = sorted(self.output_dir.glob(pattern), reverse=True)
        return reports[0] if reports else None
