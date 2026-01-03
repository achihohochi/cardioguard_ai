"""
CardioGuard_AI Streamlit Application
Main user interface for fraud investigators.
"""

import streamlit as st
import asyncio
from pathlib import Path
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from workflow import analyze_provider_fraud_risk
from services.export_service import ExportService
from services.fraud_financial_service import FraudFinancialService
from models import FraudFinancialData
from config import validate_config


# Page configuration
st.set_page_config(
    page_title="CardioGuard AI - Fraud Investigation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize services
export_service = ExportService()
fraud_financial_service = FraudFinancialService()


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
        - Web search (legal/court records)
        
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
        - Web Search (Legal Records)
        
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
                
                # Data Sources Status
                st.subheader("📊 Data Sources")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cms_status = "✅" if report.data_sources.get("cms", False) else "❌"
                    st.write(f"{cms_status} **CMS**")
                
                with col2:
                    oig_status = "✅" if report.data_sources.get("oig", False) else "❌"
                    st.write(f"{oig_status} **OIG**")
                
                with col3:
                    nppes_status = "✅" if report.data_sources.get("nppes", False) else "❌"
                    st.write(f"{nppes_status} **NPPES**")
                
                with col4:
                    web_search_status = "✅" if report.data_sources.get("web_search", False) else "❌"
                    st.write(f"{web_search_status} **Web Search**")
                
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
                            # Show URL link for Web Search evidence
                            if evidence.data_source == "Web Search" and evidence.url:
                                st.write(f"**Source URL:** [{evidence.url}]({evidence.url})")
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
                
                st.markdown("---")
                
                # Fraud Financial Data Section
                st.subheader("💰 Fraud Financial Data")
                
                # Load existing financial data if available
                existing_financial_data = fraud_financial_service.get_financial_data(provider_npi)
                
                if existing_financial_data:
                    st.info(f"**Existing Financial Data Found**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if existing_financial_data.estimated_fraud_amount:
                            st.metric("Estimated Fraud", f"${existing_financial_data.estimated_fraud_amount:,.2f}")
                    with col2:
                        if existing_financial_data.settlement_amount:
                            st.metric("Settlement Amount", f"${existing_financial_data.settlement_amount:,.2f}")
                    with col3:
                        if existing_financial_data.restitution_amount:
                            st.metric("Restitution", f"${existing_financial_data.restitution_amount:,.2f}")
                    
                    if existing_financial_data.total_fraud_impact > 0:
                        st.success(f"**Total Fraud Impact: ${existing_financial_data.total_fraud_impact:,.2f}**")
                    
                    if existing_financial_data.investigation_year:
                        st.write(f"**Investigation Year:** {existing_financial_data.investigation_year}")
                    if existing_financial_data.source:
                        st.write(f"**Source:** {existing_financial_data.source}")
                
                # Input form for new/updated financial data
                with st.expander("➕ Add/Update Fraud Financial Data", expanded=not existing_financial_data):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        estimated_fraud = st.number_input(
                            "Estimated Fraud Amount ($)",
                            min_value=0.0,
                            value=float(existing_financial_data.estimated_fraud_amount) if existing_financial_data and existing_financial_data.estimated_fraud_amount else 0.0,
                            step=1000.0,
                            help="Total estimated fraud amount"
                        )
                        
                        settlement_amount = st.number_input(
                            "Settlement Amount ($)",
                            min_value=0.0,
                            value=float(existing_financial_data.settlement_amount) if existing_financial_data and existing_financial_data.settlement_amount else 0.0,
                            step=1000.0,
                            help="Settlement amount if available"
                        )
                        
                        restitution_amount = st.number_input(
                            "Restitution Amount ($)",
                            min_value=0.0,
                            value=float(existing_financial_data.restitution_amount) if existing_financial_data and existing_financial_data.restitution_amount else 0.0,
                            step=1000.0,
                            help="Court-ordered restitution"
                        )
                    
                    with col2:
                        investigation_year = st.number_input(
                            "Investigation Year",
                            min_value=2000,
                            max_value=2030,
                            value=existing_financial_data.investigation_year if existing_financial_data and existing_financial_data.investigation_year else datetime.now().year,
                            step=1,
                            help="Year fraud was discovered/investigated"
                        )
                        
                        source = st.text_input(
                            "Source",
                            value=existing_financial_data.source if existing_financial_data and existing_financial_data.source else "",
                            placeholder="e.g., Court records, Settlement, Investigation",
                            help="Source of financial data"
                        )
                        
                        notes = st.text_area(
                            "Notes",
                            value=existing_financial_data.notes if existing_financial_data and existing_financial_data.notes else "",
                            placeholder="Additional notes about fraud amounts",
                            height=100
                        )
                    
                    if st.button("💾 Save Financial Data", type="primary"):
                        if estimated_fraud > 0 or settlement_amount > 0 or restitution_amount > 0:
                            financial_data = FraudFinancialData(
                                estimated_fraud_amount=estimated_fraud if estimated_fraud > 0 else None,
                                settlement_amount=settlement_amount if settlement_amount > 0 else None,
                                restitution_amount=restitution_amount if restitution_amount > 0 else None,
                                investigation_year=investigation_year,
                                source=source if source else None,
                                notes=notes if notes else None
                            )
                            
                            fraud_financial_service.save_financial_data(provider_npi, financial_data)
                            
                            # Update report with financial data
                            report.fraud_financial_data = financial_data
                            
                            st.success(f"✅ Financial data saved! Total impact: ${financial_data.total_fraud_impact:,.2f}")
                            st.rerun()
                        else:
                            st.warning("Please enter at least one financial amount.")
                
                st.markdown("---")
                
                # PDF Export
                st.subheader("📄 Export Report")
                try:
                    # Load financial data into report if available
                    if not report.fraud_financial_data:
                        report.fraud_financial_data = fraud_financial_service.get_financial_data(provider_npi)
                    
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
    
    # Annual Summary Section (in sidebar)
    with st.sidebar:
        st.markdown("---")
        st.header("📊 Annual Summary")
        
        current_year = datetime.now().year
        selected_year = st.selectbox(
            "Select Year",
            options=list(range(2020, current_year + 2)),
            index=len(list(range(2020, current_year + 2))) - 2,
            help="View total fraud impact for selected year"
        )
        
        annual_total = fraud_financial_service.get_annual_total(selected_year)
        
        if annual_total > 0:
            st.metric(
                f"Total Fraud Impact ({selected_year})",
                f"${annual_total:,.2f}",
                help="Sum of all fraud amounts recorded for this year"
            )
            
            provider_count = len([
                npi for npi in fraud_financial_service.get_all_providers_with_financial_data()
                if any(
                    entry.investigation_year == selected_year 
                    for entry in fraud_financial_service.get_all_financial_data(npi)
                )
            ])
            
            st.caption(f"{provider_count} provider(s) with financial data")
        else:
            st.info(f"No financial data recorded for {selected_year}")
    
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
