# CardioGuard_AI - Technical Requirements (Free Tools + FI Focus)

## 🎯 Technical Overview

**Objective:** Build healthcare fraud detection system using multi-agent architecture with 100% free tools  
**Timeline:** 1-day development  
**User:** Fraud Investigator (FI) only  
**Budget:** <$5/month total operating cost  

## 🏗️ System Architecture

### Multi-Agent Framework
```
Input Layer → Research Agent → Analysis Engine → Report Generator → Quality Validator → Output Layer
```

### Core Technology Stack (Free Tools)
- **Frontend:** Streamlit 1.31.0 (open source)
- **AI Engine:** Claude Haiku (lowest cost model)
- **Vector Database:** Pinecone Free Tier (1M vectors)
- **Data Processing:** Pandas, NumPy (open source)
- **Workflow:** Python asyncio (built-in)
- **Export:** ReportLab (open source PDF)

## 📊 Data Architecture

### Data Sources (100% Free/Public)
```python
DATA_SOURCES = {
    "cms_open_data": {
        "url": "https://data.cms.gov/api/1/",
        "cost": "free",
        "rate_limit": "reasonable_usage",
        "data_types": ["provider_utilization", "peer_baselines"]
    },
    "oig_exclusions": {
        "url": "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv",
        "cost": "free", 
        "update_frequency": "monthly",
        "data_types": ["exclusion_status", "enforcement_actions"]
    },
    "nppes_registry": {
        "url": "https://download.cms.gov/nppes/",
        "cost": "free",
        "data_types": ["provider_credentials", "practice_info"]
    }
}
```

### Data Models
```python
class ProviderProfile:
    npi: str
    name: str
    specialty: str
    location: dict
    utilization_data: dict
    risk_factors: list
    risk_score: float

class FraudEvidence:
    evidence_type: str
    description: str
    statistical_significance: float
    data_source: str
    regulatory_citation: str

class InvestigationReport:
    provider_npi: str
    risk_score: int  # 0-100
    priority_level: str  # low, medium, high
    evidence_summary: list[FraudEvidence]
    recommendations: list[str]
    generated_at: datetime
```

## 🤖 Agent Specifications

### Research Agent
```python
# Purpose: Multi-source healthcare data collection
# Input: Provider NPI
# Output: Comprehensive provider profile
# Technology: Existing agent patterns adapted for healthcare

async def collect_provider_intelligence(npi: str) -> ProviderProfile:
    # Parallel data collection from CMS + OIG + NPPES
    # Data fusion and quality validation
    # Evidence compilation for analysis
```

### Pattern Analyzer
```python
# Purpose: Fraud pattern detection and risk scoring
# Input: ProviderProfile
# Output: Risk assessment with evidence
# Technology: Statistical analysis + machine learning patterns

def analyze_fraud_patterns(provider: ProviderProfile) -> dict:
    # Statistical anomaly detection vs peer baselines
    # Temporal pattern analysis (billing clustering)
    # Geographic anomaly identification
    # Risk score calculation (0-100 scale)
```

### Report Writer
```python
# Purpose: Investigation report generation
# Input: Analysis results
# Output: Professional investigation report
# Technology: LLM-powered narrative generation

async def generate_investigation_report(analysis: dict) -> InvestigationReport:
    # Evidence summarization
    # Regulatory citation inclusion
    # Professional formatting for FI audience
    # Actionable recommendations
```

### Quality Checker
```python
# Purpose: Report validation and quality assurance
# Input: Generated report
# Output: Quality-validated report
# Technology: Automated quality checks + validation rules

def validate_report_quality(report: InvestigationReport) -> bool:
    # Completeness validation
    # Evidence accuracy checking
    # Regulatory compliance verification
    # Professional standard compliance
```

## 💾 Vector Database Integration (Pinecone Free)

### Configuration
```python
PINECONE_CONFIG = {
    "index_name": "cardioguard-vectors",
    "dimension": 1536,  # OpenAI embedding size
    "metric": "cosine",
    "pod_type": "starter",  # Free tier
    "max_vectors": 1000000,  # Free limit
    "cost": "$0/month"
}
```

### Use Cases
- **Provider Pattern Storage:** Historical fraud patterns for similarity matching
- **Evidence Embedding:** Regulatory citations and case precedents  
- **Peer Comparison:** Similar provider profiles for baseline analysis

## 🔄 Workflow Orchestration

### Main Analysis Workflow
```python
async def analyze_provider_fraud_risk(npi: str) -> InvestigationReport:
    # Step 1: Research Agent - Data Collection
    provider_profile = await research_agent.collect_intelligence(npi)
    
    # Step 2: Pattern Analyzer - Fraud Detection
    risk_analysis = pattern_analyzer.analyze_patterns(provider_profile)
    
    # Step 3: Report Writer - Report Generation  
    draft_report = await report_writer.generate_report(risk_analysis)
    
    # Step 4: Quality Checker - Validation
    final_report = quality_checker.validate_and_finalize(draft_report)
    
    return final_report
```

### Performance Optimization
- **Parallel Processing:** Simultaneous data source queries
- **Caching Strategy:** Local cache for repeated queries
- **Batch Processing:** Multiple providers when needed
- **Error Handling:** Graceful degradation for missing data

## 🎨 User Interface (Streamlit)

### Single-Page Application
```python
# Main interface components
def main():
    st.title("🏥 CardioGuard_AI - Fraud Investigation")
    
    # Input Section
    provider_npi = st.text_input("Provider NPI")
    
    # Analysis Trigger
    if st.button("Analyze Provider"):
        with st.spinner("Analyzing provider fraud risk..."):
            result = analyze_provider_fraud_risk(provider_npi)
        display_results(result)
    
    # Results Display
    def display_results(report):
        # Risk score visualization
        # Evidence summary
        # Investigation recommendations
        # PDF export button
```

### User Experience Requirements
- **Loading Time:** <30 seconds for complete analysis
- **Interface Simplicity:** Single page with clear workflow
- **Error Messages:** Helpful guidance for invalid inputs
- **Professional Output:** Suitable for compliance team review

## 📈 Performance Specifications

### Response Time Requirements
- **Provider Lookup:** <5 seconds
- **Pattern Analysis:** <15 seconds  
- **Report Generation:** <10 seconds
- **Total Workflow:** <30 seconds

### Accuracy Requirements
- **Fraud Detection Rate:** >90% on known cases
- **False Positive Rate:** <5% on normal providers
- **Evidence Relevance:** >95% pertinent to investigation

### Cost Requirements
- **Claude API Usage:** <$5/month (Haiku model)
- **Pinecone Storage:** $0/month (free tier)
- **Infrastructure:** $0/month (local deployment)
- **Total Operating Cost:** <$5/month

## 🔧 Configuration Management

### Environment Variables
```bash
# API Configuration
ANTHROPIC_API_KEY=your_claude_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env

# Cost Controls
MAX_MONTHLY_API_COST=5.00
PREFERRED_MODEL=claude-3-haiku-20240307
MAX_TOKENS_PER_REQUEST=1000

# Data Sources
CMS_API_BASE_URL=https://data.cms.gov/api/1/
OIG_EXCLUSIONS_URL=https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv

# Application
LOG_LEVEL=INFO
CACHE_DURATION_HOURS=24
STREAMLIT_PORT=8501
```

### Security Requirements
- **Data Protection:** Public data only, no PHI processing
- **API Security:** Environment variable storage for keys
- **Local Storage:** Encrypted cache for sensitive analysis results
- **Access Control:** Single-user local deployment (no web exposure)

## 🧪 Testing Requirements

### Validation Test Cases
```python
TEST_CASES = {
    "known_fraud_provider": {
        "npi": "1234567890",
        "expected_risk_score": ">80",
        "expected_priority": "high",
        "validation_criteria": ["billing_anomaly_detected", "report_generated"]
    },
    "normal_provider": {
        "npi": "0987654321", 
        "expected_risk_score": "<30",
        "expected_priority": "low",
        "validation_criteria": ["no_false_positive", "report_generated"]
    }
}
```

### Performance Testing
- **Load Testing:** 50+ consecutive analyses without degradation
- **Memory Testing:** <2GB RAM usage during operation
- **Speed Testing:** Consistent <30 second response times

## 📦 Deployment Requirements

### Local Development Deployment
```bash
# Simple deployment process
pip install -r requirements.txt
streamlit run app.py

# Access via: http://localhost:8501
```

### Production Considerations (Future)
- **Cloud Deployment:** Streamlit Cloud (free tier available)
- **Scaling:** Horizontal scaling for multiple FI users
- **Monitoring:** Usage tracking and performance monitoring
- **Backup:** Investigation result archival

## ✅ Technical Success Criteria

### Functional Validation
- [ ] All agents execute successfully in workflow
- [ ] CMS and OIG data integration working
- [ ] Fraud pattern detection algorithms functional
- [ ] Streamlit UI responsive and intuitive
- [ ] PDF report export working properly

### Performance Validation
- [ ] <30 second end-to-end analysis time
- [ ] >90% accuracy on known fraud test cases
- [ ] <5% false positive rate on normal providers
- [ ] Memory usage <2GB during operation
- [ ] Cost tracking under $5/month budget

### Quality Validation
- [ ] Investigation reports meet professional standards
- [ ] Evidence citations properly formatted
- [ ] Regulatory compliance maintained
- [ ] User experience suitable for daily FI use
- [ ] Error handling provides helpful guidance

---

*Technical requirements optimized for 1-day development using only free tools and focused on Fraud Investigator needs.*
