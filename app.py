"""
CardioGuard_AI Streamlit Application
Main user interface for fraud investigators.
"""

import streamlit as st
import asyncio
from pathlib import Path
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from workflow import analyze_provider_fraud_risk
from services.export_service import ExportService
from config import validate_config


# Page configuration
st.set_page_config(
    page_title="CardioGuard AI - Fraud Investigation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize export service
export_service = ExportService()


def main():
    """Main Streamlit application."""
    st.title("🏥 CardioGuard AI - Healthcare Fraud Investigation")
    st.markdown("---")
    
    # Configuration validation
    is_valid, errors = validate_config()
    if not is_valid:
        st.error("⚠️ Configuration Error")
        st.error("Please configure the following in your .env file:")
        for error in errors:
            st.error(f"- {error}")
        st.stop()
    
    # Sidebar for information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        **CardioGuard AI** analyzes healthcare providers for fraud risk using:
        - CMS utilization data
        - OIG exclusion database
        - NPPES provider registry
        
        Enter a provider NPI to begin investigation.
        """)
        
        st.markdown("---")
        st.markdown("**Risk Score Guide:**")
        st.markdown("- 🟢 **Low (0-29)**: Routine monitoring")
        st.markdown("- 🟡 **Medium (30-69)**: Further review recommended")
        st.markdown("- 🔴 **High (70-100)**: Immediate investigation")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Provider Analysis")
        
        # Provider input
        provider_npi = st.text_input(
            "Provider NPI",
            placeholder="Enter 10-digit National Provider Identifier",
            help="Enter the 10-digit NPI number for the provider to investigate"
        )
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Provider", type="primary", use_container_width=True)
    
    with col2:
        st.header("Quick Info")
        st.info("""
        **Processing Time:** ~30 seconds
        
        **Data Sources:**
        - CMS Open Data
        - OIG Exclusions
        - NPPES Registry
        
        **Output:** Investigation report with risk score and evidence
        """)
    
    # Analysis results
    if analyze_button:
        if not provider_npi:
            st.error("⚠️ Please enter a provider NPI")
            st.stop()
        
        if not provider_npi.isdigit() or len(provider_npi) != 10:
            st.error("⚠️ Invalid NPI format. Must be exactly 10 digits.")
            st.stop()
        
        # Run analysis with progress indicator
        with st.spinner("🔍 Analyzing provider fraud risk... This may take up to 30 seconds."):
            try:
                # Run async workflow
                report = asyncio.run(analyze_provider_fraud_risk(provider_npi))
                
                # Display results
                st.success("✅ Analysis Complete!")
                st.markdown("---")
                
                # Risk score display
                col_score, col_priority = st.columns(2)
                
                with col_score:
                    # Color-coded risk score
                    if report.risk_score >= 70:
                        score_color = "🔴"
                        priority_color = "danger"
                    elif report.risk_score >= 30:
                        score_color = "🟡"
                        priority_color = "warning"
                    else:
                        score_color = "🟢"
                        priority_color = "success"
                    
                    st.metric(
                        "Risk Score",
                        f"{score_color} {report.risk_score}/100"
                    )
                
                with col_priority:
                    st.metric(
                        "Priority Level",
                        report.priority_level.upper()
                    )
                
                st.markdown("---")
                
                # Executive Summary
                st.subheader("📋 Executive Summary")
                st.write(report.executive_summary)
                st.markdown("---")
                
                # Evidence Summary
                st.subheader("🔍 Evidence Summary")
                if report.evidence_summary:
                    for i, evidence in enumerate(report.evidence_summary, 1):
                        with st.expander(f"Evidence {i}: {evidence.evidence_type.replace('_', ' ').title()}"):
                            st.write(f"**Description:** {evidence.description}")
                            st.write(f"**Severity:** {evidence.severity.upper()}")
                            st.write(f"**Data Source:** {evidence.data_source}")
                            st.write(f"**Statistical Significance:** {evidence.statistical_significance:.2f}")
                            if evidence.regulatory_citation:
                                st.write(f"**Regulatory Citation:** {evidence.regulatory_citation}")
                else:
                    st.info("No evidence items found.")
                
                st.markdown("---")
                
                # Recommendations
                st.subheader("💡 Recommendations")
                if report.recommendations:
                    for i, recommendation in enumerate(report.recommendations, 1):
                        st.write(f"{i}. {recommendation}")
                else:
                    st.info("No recommendations available.")
                
                st.markdown("---")
                
                # Regulatory Citations
                if report.regulatory_citations:
                    st.subheader("📚 Regulatory Citations")
                    for citation in report.regulatory_citations:
                        st.write(f"- {citation}")
                    st.markdown("---")
                
                # PDF Export
                st.subheader("📄 Export Report")
                try:
                    pdf_path = export_service.export_to_pdf(report)
                    with open(pdf_path, 'rb') as pdf_file:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_file.read(),
                            file_name=pdf_path.name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Failed to generate PDF: {e}")
                    logger.error(f"PDF export failed: {e}")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                logger.error(f"Analysis failed for NPI {provider_npi}: {e}", exc_info=True)
                st.info("Please check the logs for more details or try again.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "CardioGuard AI - Healthcare Fraud Detection System | "
        "Built with Streamlit, Claude Haiku, and free healthcare APIs"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
