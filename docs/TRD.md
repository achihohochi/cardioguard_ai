# 🔧 CardioGuard AI - Technical Requirements Document (TRD)

**Version:** 2.0  
**Date:** January 2026  
**Owner:** Engineering Team  
**Status:** Ralph-Compatible Implementation Ready  

---

## 🏗️ Technical Architecture Overview

CardioGuard AI implements a **4-agent autonomous architecture** designed for seamless integration with the Ralph framework for iterative task completion and quality improvement. The system transforms manual healthcare fraud investigations into fully automated 30-second assessments.

### **Architecture Principles**
- **Agent Autonomy:** Each agent operates independently with clear responsibilities
- **Iterative Improvement:** Ralph framework enables continuous task refinement until completion
- **Fault Tolerance:** Graceful handling of API failures and data inconsistencies  
- **Scalability:** Parallel processing of multiple provider investigations
- **Observability:** Comprehensive logging and monitoring at every stage

---

## 🤖 Agent Architecture Specification

### **Agent 1: Research Agent**

#### **Purpose & Responsibilities**
- Autonomous data collection from multiple healthcare data sources
- Provider profile assembly and data validation
- Source prioritization and fallback handling

#### **Technical Implementation**
```python
class ResearchAgent(BaseAgent):
    """Autonomous provider intelligence collection agent."""
    
    async def collect_provider_intelligence(self, npi: str) -> ProviderProfile:
        """Ralph-compatible data collection with retry logic."""
        
    def validate_data_completeness(self, profile: ProviderProfile) -> bool:
        """Verify minimum data requirements for analysis."""
        
    async def enhance_incomplete_data(self, profile: ProviderProfile) -> ProviderProfile:
        """Attempt to fill data gaps from additional sources."""
```

#### **Data Sources & APIs**
| Source | API Endpoint | Timeout | Cache TTL | Retry Policy |
|--------|-------------|---------|-----------|--------------|
| **CMS Open Data** | `data.cms.gov/data-api/v1/dataset/` | 60s | 24h | 3x exponential backoff |
| **OIG Exclusions** | `oig.hhs.gov/exclusions/downloadables/UPDATED.csv` | 180s | 30d | 2x with 5s delay |  
| **NPPES Registry** | `npiregistry.cms.hhs.gov/api/` | 60s | 7d | 3x exponential backoff |
| **Web Intelligence** | DuckDuckGo API | 30s | 7d | 2x linear backoff |

#### **Ralph Integration Points**
- **Completion Criteria:** All required data fields populated OR maximum retry attempts reached
- **Quality Gate:** Data completeness score >80%
- **Retry Logic:** Missing critical data triggers additional collection attempts
- **Tool Integration:** Each API call as discrete tool with success/failure feedback

#### **Performance Requirements**
- **Target Execution Time:** <10 seconds
- **Data Completeness:** >95% for critical fields (NPI, name, specialty)
- **Error Handling:** Graceful degradation when data sources unavailable
- **Concurrent Requests:** Support 100+ parallel provider investigations

---

### **Agent 2: Pattern Analyzer Agent**

#### **Purpose & Responsibilities**  
- Statistical fraud pattern detection using multiple algorithms
- Risk score calculation with confidence intervals
- Evidence generation with statistical significance

#### **Technical Implementation**
```python
class PatternAnalyzer(BaseAgent):
    """Statistical fraud pattern detection agent."""
    
    def analyze_fraud_patterns(self, provider: ProviderProfile) -> RiskAnalysis:
        """Comprehensive pattern analysis with statistical validation."""
        
    def calculate_statistical_anomalies(self, utilization: UtilizationData) -> List[FraudEvidence]:
        """Z-score analysis for billing anomalies (threshold: 2.5σ)."""
        
    def detect_billing_clusters(self, billing_data: List[Dict]) -> List[FraudEvidence]:
        """Temporal and geographic clustering analysis."""
        
    def peer_comparison_analysis(self, provider: ProviderProfile) -> List[FraudEvidence]:
        """Compare against specialty/location peer groups."""
```

#### **Statistical Algorithms**

##### **Z-Score Anomaly Detection**
- **Purpose:** Identify statistical outliers in billing patterns
- **Threshold:** 2.5 standard deviations from mean
- **Metrics:** Services per beneficiary, total payments, unique beneficiaries
- **Implementation:** Scipy.stats with rolling window calculation

##### **Clustering Analysis**  
- **Temporal Clustering:** End-of-month/year billing spikes
- **Geographic Clustering:** Unusual patient travel patterns
- **Service Clustering:** Inappropriate service combinations
- **Algorithm:** DBSCAN with configurable epsilon and min_samples

##### **Peer Comparison**
- **Grouping Criteria:** Specialty, state, practice size, years in practice
- **Comparison Metrics:** Billing volume, service mix, payment amounts
- **Statistical Tests:** Welch's t-test for group differences
- **Significance Level:** p < 0.05 for evidence inclusion

#### **Ralph Integration Points**
- **Completion Criteria:** All analysis algorithms executed AND statistical significance achieved
- **Quality Gate:** Risk score confidence interval <10%
- **Iterative Refinement:** Low confidence triggers additional peer group analysis
- **Tool Integration:** Each algorithm as separate tool with confidence feedback

#### **Performance Requirements**
- **Target Execution Time:** <15 seconds
- **Analysis Coverage:** 100% of available data fields
- **Statistical Power:** >80% for peer comparison tests
- **Memory Usage:** <2GB for analysis computations

---

### **Agent 3: Report Writer Agent**

#### **Purpose & Responsibilities**
- Professional investigation report generation using Claude Haiku
- Structured output with regulatory citations  
- Evidence summarization with actionable recommendations

#### **Technical Implementation**
```python
class ReportWriter(BaseAgent):
    """AI-powered investigation report generation agent."""
    
    async def generate_investigation_report(self, analysis: RiskAnalysis, profile: ProviderProfile) -> InvestigationReport:
        """Generate comprehensive investigation report using Claude API."""
        
    def structure_evidence_summary(self, evidence: List[FraudEvidence]) -> Dict:
        """Organize evidence by severity and type."""
        
    def generate_recommendations(self, risk_score: float, evidence: List[FraudEvidence]) -> List[str]:
        """Create actionable recommendations based on findings."""
        
    def add_regulatory_citations(self, evidence: List[FraudEvidence]) -> Dict[str, str]:
        """Map evidence to relevant regulatory frameworks."""
```

#### **AI Model Configuration**
| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| **Model** | claude-3-haiku-20240307 | Cost-effective for report generation |
| **Max Tokens** | 1000 | Sufficient for comprehensive reports |
| **Temperature** | 0.3 | Balanced creativity with consistency |
| **System Prompt** | Structured investigation report template | Ensures consistent output format |
| **Cost Control** | $5/month maximum | Operational cost limit |

#### **Report Structure & Template**
```yaml
investigation_report:
  executive_summary:
    - provider_overview
    - risk_level_assessment  
    - key_findings_summary
    - immediate_recommendations
  
  evidence_analysis:
    high_severity_findings:
      - statistical_significance: "> 95%"
      - regulatory_impact: "high"
    medium_severity_findings:
      - statistical_significance: "90-95%"  
      - regulatory_impact: "medium"
    low_severity_findings:
      - statistical_significance: "85-90%"
      - regulatory_impact: "low"
  
  recommendations:
    immediate_actions: []
    investigation_priorities: []
    compliance_considerations: []
  
  regulatory_citations:
    applicable_statutes: []
    regulatory_guidelines: []
    precedent_cases: []
```

#### **Ralph Integration Points**
- **Completion Criteria:** Report contains all required sections AND passes quality validation
- **Quality Gate:** Report completeness score >90%
- **Iterative Improvement:** Failed validation triggers regeneration with specific feedback
- **Tool Integration:** Claude API call as tool with structured output validation

#### **Performance Requirements**
- **Target Execution Time:** <10 seconds  
- **Report Completeness:** 100% of required sections
- **Readability Score:** Flesch-Kincaid Grade Level 12-14
- **Cost Per Report:** <$0.02

---

### **Agent 4: Quality Checker Agent**

#### **Purpose & Responsibilities**
- Automated quality assurance and validation
- Report completeness verification
- Evidence backing validation
- Final approval/rejection decisions

#### **Technical Implementation**  
```python
class QualityChecker(BaseAgent):
    """Comprehensive quality assurance agent."""
    
    def validate_report_quality(self, report: InvestigationReport) -> QualityAssessment:
        """Multi-dimensional quality validation."""
        
    def check_report_completeness(self, report: InvestigationReport) -> CompletionScore:
        """Verify all required sections present and populated."""
        
    def validate_evidence_backing(self, evidence: List[FraudEvidence]) -> EvidenceScore:
        """Ensure all claims have statistical backing."""
        
    def verify_regulatory_accuracy(self, citations: Dict[str, str]) -> AccuracyScore:
        """Validate regulatory citation relevance and accuracy."""
```

#### **Quality Validation Framework**

##### **Completeness Validation**
```python
REQUIRED_SECTIONS = [
    'executive_summary',
    'evidence_summary', 
    'recommendations',
    'regulatory_citations'
]

COMPLETENESS_CHECKS = {
    'executive_summary': {'min_words': 100, 'required_elements': ['risk_score', 'key_findings']},
    'evidence_summary': {'min_evidence': 1, 'severity_distribution': True},
    'recommendations': {'min_recommendations': 3, 'actionable_format': True},
    'regulatory_citations': {'min_citations': 1, 'valid_references': True}
}
```

##### **Evidence Validation**
```python
EVIDENCE_VALIDATION = {
    'statistical_significance': {'min_p_value': 0.05, 'confidence_interval': True},
    'data_backing': {'source_verification': True, 'calculation_audit': True},
    'severity_justification': {'threshold_compliance': True, 'impact_assessment': True}
}
```

##### **Quality Scoring Matrix**
| Dimension | Weight | Threshold | Measurement |
|-----------|--------|-----------|-------------|
| **Completeness** | 40% | >90% | Section presence and content depth |
| **Evidence Quality** | 30% | >85% | Statistical significance and backing |
| **Regulatory Accuracy** | 20% | >95% | Citation relevance and correctness |
| **Readability** | 10% | >80% | Clarity and professional presentation |
| **Overall Threshold** | 100% | >80% | Weighted average for approval |

#### **Ralph Integration Points**
- **Completion Criteria:** Quality score >80% AND all validation checks passed
- **Feedback Loop:** Specific quality issues returned to appropriate agents
- **Iterative Improvement:** Failed validation triggers targeted improvements
- **Tool Integration:** Each validation check as discrete tool with pass/fail result

#### **Performance Requirements**
- **Target Execution Time:** <5 seconds
- **Validation Coverage:** 100% of report elements
- **False Positive Rate:** <5% (incorrect rejections)
- **False Negative Rate:** <2% (approved low-quality reports)

---

## 🔄 Ralph Framework Integration

### **Ralph Loop Implementation**

#### **Core Ralph Agent Configuration**
```typescript
const cardioGuardAgent = new RalphLoopAgent({
  model: 'claude-3-sonnet-20241022',
  instructions: `You are a healthcare fraud investigation coordinator. 
                 Complete comprehensive provider fraud analysis using available tools.
                 Mark investigation complete only when all agents have successfully 
                 completed their tasks and quality validation passes.`,
  
  tools: {
    collectProviderData: researchAgentTool,
    analyzePatterns: patternAnalyzerTool, 
    generateReport: reportWriterTool,
    validateQuality: qualityCheckerTool,
    markInvestigationComplete: completionTool
  },
  
  stopWhen: iterationCountIs(10),
  
  verifyCompletion: async ({ result }) => {
    // Check if investigation marked complete with quality approval
    for (const step of result.steps) {
      for (const toolResult of step.toolResults) {
        if (toolResult.toolName === 'markInvestigationComplete' && 
            toolResult.result.qualityApproved === true) {
          return { 
            complete: true, 
            reason: 'Investigation completed with quality approval',
            metrics: toolResult.result.metrics
          };
        }
      }
    }
    return { 
      complete: false, 
      reason: 'Continue investigation - quality criteria not met' 
    };
  }
});
```

#### **Agent Tool Implementations**

##### **Research Agent Tool**
```typescript
const researchAgentTool = tool({
  description: 'Collect comprehensive provider intelligence from all data sources',
  parameters: z.object({
    npi: z.string().regex(/^\d{10}$/, "NPI must be 10 digits"),
    enhance_data: z.boolean().default(false)
  }),
  execute: async ({ npi, enhance_data }) => {
    const agent = new ResearchAgent();
    try {
      let profile = await agent.collect_provider_intelligence(npi);
      
      // Check completion criteria
      const completeness = agent.validate_data_completeness(profile);
      if (completeness < 0.8 && enhance_data) {
        profile = await agent.enhance_incomplete_data(profile);
      }
      
      return {
        success: true,
        profile: profile,
        completeness_score: completeness,
        complete: completeness > 0.8
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        complete: false
      };
    }
  }
});
```

##### **Pattern Analyzer Tool**
```typescript
const patternAnalyzerTool = tool({
  description: 'Analyze fraud patterns and calculate risk score with statistical validation',
  parameters: z.object({
    provider_profile: z.object({}).passthrough(),
    confidence_threshold: z.number().default(0.9)
  }),
  execute: async ({ provider_profile, confidence_threshold }) => {
    const analyzer = new PatternAnalyzer();
    try {
      const analysis = analyzer.analyze_fraud_patterns(provider_profile);
      
      // Check statistical confidence
      const confidence = analysis.confidence_score;
      const complete = confidence >= confidence_threshold;
      
      return {
        success: true,
        risk_analysis: analysis,
        confidence_score: confidence,
        complete: complete,
        needs_refinement: !complete
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        complete: false
      };
    }
  }
});
```

##### **Quality Validation Tool**
```typescript
const qualityCheckerTool = tool({
  description: 'Validate investigation report quality and approve for completion',
  parameters: z.object({
    investigation_report: z.object({}).passthrough(),
    quality_threshold: z.number().default(0.8)
  }),
  execute: async ({ investigation_report, quality_threshold }) => {
    const checker = new QualityChecker();
    try {
      const assessment = checker.validate_report_quality(investigation_report);
      
      const approved = assessment.overall_score >= quality_threshold;
      
      return {
        success: true,
        quality_score: assessment.overall_score,
        validation_details: assessment.details,
        approved: approved,
        complete: approved,
        improvement_suggestions: approved ? [] : assessment.suggestions
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        complete: false
      };
    }
  }
});
```

### **Completion Verification Logic**

#### **Multi-Stage Completion Criteria**
```python
def verify_investigation_completion(result):
    """Multi-stage completion verification for Ralph loop."""
    
    completion_stages = {
        'data_collection': False,
        'pattern_analysis': False, 
        'report_generation': False,
        'quality_validation': False
    }
    
    # Track completion of each stage
    for step in result.steps:
        for tool_result in step.toolResults:
            tool_name = tool_result.toolName
            
            if tool_name == 'collectProviderData' and tool_result.result.complete:
                completion_stages['data_collection'] = True
                
            elif tool_name == 'analyzePatterns' and tool_result.result.complete:
                completion_stages['pattern_analysis'] = True
                
            elif tool_name == 'generateReport' and tool_result.result.complete:
                completion_stages['report_generation'] = True
                
            elif tool_name == 'validateQuality' and tool_result.result.approved:
                completion_stages['quality_validation'] = True
    
    # Investigation complete only when all stages successful
    all_complete = all(completion_stages.values())
    
    if all_complete:
        return {
            'complete': True,
            'reason': 'All investigation stages completed successfully',
            'completion_stages': completion_stages
        }
    else:
        incomplete_stages = [stage for stage, complete in completion_stages.items() if not complete]
        return {
            'complete': False,
            'reason': f'Incomplete stages: {", ".join(incomplete_stages)}',
            'completion_stages': completion_stages
        }
```

#### **Iterative Improvement Logic**
```python
def get_improvement_feedback(result, completion_check):
    """Generate specific feedback for incomplete stages."""
    
    feedback = []
    stages = completion_check['completion_stages']
    
    if not stages['data_collection']:
        feedback.append("Data collection incomplete. Try enhancing data from additional sources.")
        
    if not stages['pattern_analysis']:
        feedback.append("Pattern analysis needs refinement. Consider expanding peer comparison groups.")
        
    if not stages['report_generation']:
        feedback.append("Report generation incomplete. Ensure all required sections are included.")
        
    if not stages['quality_validation']:
        feedback.append("Quality validation failed. Address specific quality issues and regenerate.")
    
    return feedback
```

---

## 🔧 System Implementation Details

### **Technology Stack**

#### **Core Framework**
- **Python 3.11+:** Primary runtime environment
- **Ralph Loop Agent:** Autonomous task completion framework
- **Pydantic:** Data validation and type safety
- **Loguru:** Structured logging and observability

#### **AI & Analytics**
- **Anthropic Claude:** Report generation and natural language processing
- **NumPy/SciPy:** Statistical analysis and computations
- **Pandas:** Data manipulation and analysis
- **Scikit-learn:** Machine learning algorithms for pattern detection

#### **Data & APIs**
- **aiohttp:** Asynchronous HTTP client for API requests
- **Requests:** Synchronous HTTP client for simple API calls
- **BeautifulSoup4:** Web scraping for additional intelligence
- **DuckDuckGo Search:** Web search integration

#### **User Interface**
- **Streamlit:** Web application framework
- **Plotly:** Interactive data visualizations
- **ReportLab:** PDF report generation
- **Streamlit-AgGrid:** Advanced data grids

### **Database & Caching Strategy**

#### **Local File-Based Storage**
```python
# Cache configuration
CACHE_STRUCTURE = {
    'data/cache/cms/': {
        'purpose': 'CMS provider utilization data',
        'ttl': '24 hours',
        'format': 'JSON'
    },
    'data/cache/oig/': {
        'purpose': 'OIG exclusion database',  
        'ttl': '30 days',
        'format': 'CSV'
    },
    'data/cache/nppes/': {
        'purpose': 'NPPES provider registry data',
        'ttl': '7 days', 
        'format': 'JSON'
    },
    'data/cache/analysis/': {
        'purpose': 'Completed analysis results',
        'ttl': '1 hour',
        'format': 'Pickle'
    }
}
```

#### **Cache Management**
- **LRU Eviction:** Least recently used data removed when cache full
- **Background Refresh:** Automatic cache refresh before expiration
- **Cache Invalidation:** Manual cache clearing for data quality issues
- **Compression:** GZIP compression for large datasets

### **API Integration Specifications**

#### **CMS Open Data API**
```python
CMS_API_CONFIG = {
    'base_url': 'https://data.cms.gov/data-api/v1/dataset/',
    'dataset_id': '92396110-2aed-4d63-a6a2-5d6207d46a29',
    'timeout': 60,
    'retry_attempts': 3,
    'retry_delay': 2.0,
    'rate_limit': '100 requests/hour',
    'response_format': 'JSON'
}
```

#### **OIG Exclusion Database**
```python
OIG_API_CONFIG = {
    'url': 'https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv',
    'timeout': 180,
    'retry_attempts': 2,
    'retry_delay': 5.0,
    'download_size': '~15MB',
    'update_frequency': 'Monthly'
}
```

#### **NPPES Registry API**  
```python
NPPES_API_CONFIG = {
    'base_url': 'https://npiregistry.cms.hhs.gov/api/',
    'timeout': 60,
    'retry_attempts': 3,
    'retry_delay': 2.0,
    'rate_limit': '1200 requests/hour',
    'response_format': 'JSON'
}
```

#### **Anthropic Claude API**
```python
CLAUDE_API_CONFIG = {
    'model': 'claude-3-haiku-20240307',
    'max_tokens': 1000,
    'temperature': 0.3,
    'timeout': 30,
    'retry_attempts': 2,
    'cost_limit': '$5.00/month',
    'usage_tracking': True
}
```

---

## 📊 Performance & Monitoring

### **Performance Targets**

| Component | Target Latency | Success Rate | Error Budget |
|-----------|----------------|--------------|--------------|
| **Research Agent** | <10s | >99% | 1% |
| **Pattern Analyzer** | <15s | >98% | 2% |
| **Report Writer** | <10s | >97% | 3% |
| **Quality Checker** | <5s | >99% | 1% |
| **Overall Investigation** | <30s | >95% | 5% |

### **Monitoring & Observability**

#### **Application Metrics**
```python
METRICS_TO_TRACK = {
    'investigation_duration': 'histogram',
    'agent_execution_time': 'histogram', 
    'api_response_time': 'histogram',
    'error_rate': 'counter',
    'quality_score_distribution': 'histogram',
    'cache_hit_rate': 'gauge',
    'cost_per_investigation': 'gauge',
    'concurrent_investigations': 'gauge'
}
```

#### **Business Metrics**
```python
BUSINESS_METRICS = {
    'fraud_detection_rate': 'percentage',
    'false_positive_rate': 'percentage',
    'investigator_productivity': 'rate',
    'cost_savings': 'dollar_amount',
    'user_satisfaction': 'score'
}
```

#### **Logging Strategy**
```python
# Structured logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '{time} | {level} | {name}:{function}:{line} | {message} | {extra}',
    'retention': '30 days',
    'rotation': '100MB',
    'serialization': 'JSON'
}

# Log correlation across agents
LOG_CORRELATION = {
    'investigation_id': 'UUID for tracking across agents',
    'npi': 'Provider identifier for business correlation',
    'agent_name': 'Source agent for debugging',
    'execution_stage': 'Current stage in investigation pipeline'
}
```

---

## 🛡️ Security & Reliability

### **Security Implementation**

#### **API Key Management**
```python
# Secure environment variable handling
SECURITY_CONFIG = {
    'api_key_storage': '.env file with 600 permissions',
    'key_rotation': 'Manual rotation recommended quarterly',
    'key_validation': 'Startup validation with test calls',
    'key_exposure_prevention': '.env in .gitignore'
}
```

#### **Data Protection**
```python
DATA_PROTECTION = {
    'encryption_at_rest': 'OS-level file system encryption',
    'encryption_in_transit': 'TLS 1.2+ for all API calls',
    'data_retention': 'Configurable cache TTL',
    'data_anonymization': 'Optional NPI hashing for reporting'
}
```

#### **Access Control**
```python
ACCESS_CONTROL = {
    'authentication': 'Local deployment - OS-level security',
    'authorization': 'File system permissions',
    'audit_logging': 'All API calls and user actions logged',
    'session_management': 'Streamlit built-in session handling'
}
```

### **Reliability & Fault Tolerance**

#### **Error Handling Strategy**
```python
ERROR_HANDLING = {
    'api_failures': {
        'strategy': 'Exponential backoff with circuit breaker',
        'max_retries': 3,
        'fallback': 'Graceful degradation with partial data'
    },
    'data_quality_issues': {
        'strategy': 'Validation with user notification',
        'fallback': 'Continue with available data'
    },
    'model_failures': {
        'strategy': 'Retry with alternative prompts',
        'fallback': 'Template-based report generation'
    }
}
```

#### **Circuit Breaker Implementation**
```python
class CircuitBreaker:
    """Circuit breaker for external API calls."""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e
```

---

## 🚀 Deployment & DevOps

### **Deployment Architecture**

#### **Local Development**
```bash
# Development setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure API keys
streamlit run app.py
```

#### **Production Deployment Options**

##### **Option 1: Docker Containerization**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

##### **Option 2: Cloud Deployment (Render/Heroku)**
```yaml
# render.yaml
services:
  - type: web
    name: cardioguard-ai
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: "3.11"
```

### **CI/CD Pipeline**

#### **GitHub Actions Workflow**
```yaml
name: CardioGuard AI CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=./ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security scan
        run: |
          pip install bandit safety
          bandit -r . -x tests/
          safety check
  
  deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          # Deployment commands
          echo "Deploy to production environment"
```

### **Environment Configuration**

#### **Development Environment**
```env
# Development .env template
ANTHROPIC_API_KEY=sk-ant-api03-...
PINECONE_API_KEY=your-pinecone-key  # Optional
PINECONE_ENVIRONMENT=us-west1-gcp   # Optional

# Development settings
LOG_LEVEL=DEBUG
MAX_MONTHLY_API_COST=10.00
CACHE_DURATION_HOURS=1

# API timeouts (longer for development)
CMS_API_TIMEOUT=120
NPPES_API_TIMEOUT=120
OIG_API_TIMEOUT=300
```

#### **Production Environment**
```env
# Production .env template
ANTHROPIC_API_KEY=sk-ant-api03-...

# Production settings
LOG_LEVEL=INFO
MAX_MONTHLY_API_COST=5.00
CACHE_DURATION_HOURS=24

# API timeouts (optimized for production)
CMS_API_TIMEOUT=60
NPPES_API_TIMEOUT=60
OIG_API_TIMEOUT=180
```

---

## 🧪 Testing Strategy

### **Unit Testing**

#### **Agent Testing Framework**
```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

class TestResearchAgent:
    """Unit tests for Research Agent functionality."""
    
    @pytest.fixture
    def mock_cms_service(self):
        mock = AsyncMock()
        mock.get_provider_utilization.return_value = {
            'npi': '1234567890',
            'services': 150,
            'beneficiaries': 100
        }
        return mock
    
    @pytest.mark.asyncio
    async def test_collect_provider_intelligence_success(self, mock_cms_service):
        """Test successful provider intelligence collection."""
        agent = ResearchAgent()
        agent.data_service.cms_service = mock_cms_service
        
        result = await agent.collect_provider_intelligence('1234567890')
        
        assert result.npi == '1234567890'
        assert result.utilization_data is not None
        mock_cms_service.get_provider_utilization.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_collect_provider_intelligence_api_failure(self, mock_cms_service):
        """Test graceful handling of API failures."""
        mock_cms_service.get_provider_utilization.side_effect = Exception("API Error")
        
        agent = ResearchAgent()
        agent.data_service.cms_service = mock_cms_service
        
        result = await agent.collect_provider_intelligence('1234567890')
        
        assert result.npi == '1234567890'
        assert result.utilization_data is None  # Graceful degradation
```

### **Integration Testing**

#### **End-to-End Workflow Testing**
```python
class TestWorkflowIntegration:
    """Integration tests for complete investigation workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_investigation_workflow(self):
        """Test complete investigation from NPI to report."""
        workflow = FraudInvestigationWorkflow()
        
        # Test with known provider NPI
        test_npi = '1234567890'
        
        result = await workflow.run_investigation(test_npi)
        
        # Verify complete workflow execution
        assert result.investigation_id is not None
        assert result.provider_profile.npi == test_npi
        assert result.risk_analysis.risk_score is not None
        assert result.investigation_report.executive_summary is not None
        assert result.quality_assessment.overall_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_workflow_with_data_failures(self):
        """Test workflow resilience with partial data failures."""
        # Simulate API failures
        with patch('services.cms_service.CMSDataService.get_provider_utilization') as mock_cms:
            mock_cms.side_effect = Exception("CMS API Down")
            
            workflow = FraudInvestigationWorkflow()
            result = await workflow.run_investigation('1234567890')
            
            # Should still complete with available data
            assert result.investigation_report is not None
            assert 'Limited data available' in result.investigation_report.caveats
```

### **Ralph Framework Testing**

#### **Ralph Integration Testing**
```python
class TestRalphIntegration:
    """Test Ralph framework integration and completion logic."""
    
    @pytest.mark.asyncio
    async def test_ralph_loop_completion(self):
        """Test Ralph loop completes when quality criteria met."""
        
        # Mock successful tool executions
        mock_tools = {
            'collectProviderData': Mock(return_value={'complete': True, 'success': True}),
            'analyzePatterns': Mock(return_value={'complete': True, 'confidence': 0.95}),
            'generateReport': Mock(return_value={'complete': True, 'quality_score': 0.9}),
            'validateQuality': Mock(return_value={'approved': True, 'complete': True})
        }
        
        agent = RalphLoopAgent(
            model='claude-3-sonnet-20241022',
            instructions='Complete fraud investigation',
            tools=mock_tools,
            verifyCompletion=verify_investigation_completion
        )
        
        result = await agent.loop({
            'prompt': 'Investigate provider NPI 1234567890'
        })
        
        assert result.completionReason == 'All investigation stages completed successfully'
        assert result.iterations <= 5  # Should complete efficiently
    
    @pytest.mark.asyncio 
    async def test_ralph_iterative_improvement(self):
        """Test Ralph loop iterative improvement on quality failures."""
        
        # Mock initial quality failure, then success
        quality_results = [
            {'approved': False, 'complete': False, 'quality_score': 0.6},
            {'approved': True, 'complete': True, 'quality_score': 0.85}
        ]
        
        mock_tools = {
            'validateQuality': Mock(side_effect=quality_results)
        }
        
        # Test should iterate to improve quality
        assert len(quality_results) == 2  # Should retry once
```

### **Performance Testing**

#### **Load Testing Framework**
```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Performance and load testing for CardioGuard AI."""
    
    @pytest.mark.asyncio
    async def test_concurrent_investigations(self):
        """Test system performance with concurrent investigations."""
        
        test_npis = ['1234567890', '0987654321', '1122334455']
        workflow = FraudInvestigationWorkflow()
        
        start_time = time.time()
        
        # Run concurrent investigations
        tasks = [workflow.run_investigation(npi) for npi in test_npis]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Performance assertions
        assert len(results) == 3
        assert all(r.investigation_report is not None for r in results)
        assert total_time < 60  # Should complete within 1 minute
        
        # Individual investigation should still be fast
        for result in results:
            assert result.execution_time < 30
    
    def test_memory_usage(self):
        """Test memory usage during investigation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run investigation
        workflow = FraudInvestigationWorkflow()
        asyncio.run(workflow.run_investigation('1234567890'))
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        # Memory increase should be reasonable
        assert memory_increase < 500  # Less than 500MB increase
```

---

## 📋 Configuration Management

### **Configuration Schema**
```python
from pydantic import BaseSettings, Field
from typing import Optional

class CardioGuardConfig(BaseSettings):
    """Centralized configuration management with validation."""
    
    # API Configuration
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(None, env="PINECONE_ENVIRONMENT")
    
    # Cost Controls
    max_monthly_api_cost: float = Field(5.0, env="MAX_MONTHLY_API_COST")
    preferred_model: str = Field("claude-3-haiku-20240307", env="PREFERRED_MODEL")
    max_tokens_per_request: int = Field(1000, env="MAX_TOKENS_PER_REQUEST")
    
    # Performance Tuning
    cache_duration_hours: int = Field(24, env="CACHE_DURATION_HOURS")
    cms_api_timeout: int = Field(60, env="CMS_API_TIMEOUT")
    nppes_api_timeout: int = Field(60, env="NPPES_API_TIMEOUT")
    oig_api_timeout: int = Field(180, env="OIG_API_TIMEOUT")
    
    # Ralph Framework Configuration
    ralph_max_iterations: int = Field(10, env="RALPH_MAX_ITERATIONS")
    ralph_completion_threshold: float = Field(0.8, env="RALPH_COMPLETION_THRESHOLD")
    ralph_retry_delay: float = Field(2.0, env="RALPH_RETRY_DELAY")
    
    # Quality Thresholds
    min_data_completeness: float = Field(0.8, env="MIN_DATA_COMPLETENESS")
    min_confidence_score: float = Field(0.9, env="MIN_CONFIDENCE_SCORE")  
    min_quality_score: float = Field(0.8, env="MIN_QUALITY_SCORE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## 📈 Scaling & Future Architecture

### **Horizontal Scaling Strategy**

#### **Microservice Decomposition**
```yaml
# Future microservice architecture
services:
  research-agent-service:
    purpose: "Provider data collection"
    scaling: "Stateless, auto-scaling based on CPU"
    
  pattern-analyzer-service:
    purpose: "Fraud pattern analysis"
    scaling: "CPU-intensive, vertical scaling"
    
  report-writer-service:
    purpose: "Report generation"
    scaling: "API-dependent, queue-based"
    
  quality-checker-service:
    purpose: "Quality validation"
    scaling: "Fast, stateless operations"
    
  coordination-service:
    purpose: "Ralph loop orchestration"
    scaling: "Single instance with HA"
```

#### **Database Scaling**
```yaml
# Future database architecture
databases:
  provider-cache:
    type: "Redis Cluster"
    purpose: "High-speed data caching"
    scaling: "Horizontal partitioning by NPI hash"
    
  investigation-store:
    type: "PostgreSQL"
    purpose: "Investigation results and audit trail"
    scaling: "Read replicas + partitioning by date"
    
  analytics-warehouse:
    type: "ClickHouse"  
    purpose: "Performance analytics and business intelligence"
    scaling: "Columnar storage with time-series optimization"
```

### **Performance Optimization Roadmap**

#### **Phase 1: Current Optimizations**
- ✅ Async API calls with concurrent execution
- ✅ Intelligent caching with TTL optimization
- ✅ Circuit breaker pattern for API reliability
- ✅ Connection pooling and keepalive

#### **Phase 2: Advanced Optimizations**  
- 📋 Predictive caching based on investigation patterns
- 📋 Background data refresh to minimize cache misses
- 📋 API call batching and multiplexing
- 📋 Result streaming for real-time user feedback

#### **Phase 3: ML-Powered Optimizations**
- 📋 Intelligent agent orchestration based on data availability
- 📋 Dynamic quality thresholds based on investigation complexity
- 📋 Predictive fraud scoring to reduce analysis time
- 📋 Automated pattern discovery and rule generation

---

## 📚 API Documentation

### **Ralph Tool API Specification**

#### **Research Agent Tool API**
```typescript
interface ResearchAgentTool {
  name: "collectProviderData";
  description: "Collect comprehensive provider intelligence from healthcare data sources";
  
  parameters: {
    npi: string;           // 10-digit National Provider Identifier
    enhance_data?: boolean; // Attempt additional data enhancement
    sources?: string[];    // Specific data sources to query
  };
  
  response: {
    success: boolean;
    profile?: ProviderProfile;
    completeness_score: number;     // 0.0 to 1.0
    complete: boolean;              // Meets completion criteria
    error?: string;
    execution_time: number;         // Milliseconds
  };
}
```

#### **Pattern Analyzer Tool API**
```typescript  
interface PatternAnalyzerTool {
  name: "analyzePatterns";
  description: "Analyze provider data for fraud patterns and risk indicators";
  
  parameters: {
    provider_profile: ProviderProfile;
    confidence_threshold?: number;   // Minimum confidence for completion
    analysis_depth?: 'basic' | 'comprehensive';
  };
  
  response: {
    success: boolean;
    risk_analysis?: RiskAnalysis;
    confidence_score: number;        // Statistical confidence 0.0 to 1.0  
    complete: boolean;               // Meets completion criteria
    needs_refinement: boolean;       // Suggests additional analysis
    error?: string;
    execution_time: number;
  };
}
```

#### **Report Writer Tool API**
```typescript
interface ReportWriterTool {
  name: "generateReport"; 
  description: "Generate professional investigation report using AI";
  
  parameters: {
    risk_analysis: RiskAnalysis;
    provider_profile: ProviderProfile;
    report_type?: 'summary' | 'comprehensive';
    regulatory_focus?: string[];     // Specific regulatory areas to emphasize
  };
  
  response: {
    success: boolean;
    investigation_report?: InvestigationReport;
    completeness_score: number;     // Report completeness 0.0 to 1.0
    complete: boolean;              // Report meets standards
    token_usage: number;            // Claude API tokens consumed
    cost: number;                   // Dollar cost of generation
    error?: string;
    execution_time: number;
  };
}
```

#### **Quality Checker Tool API**
```typescript
interface QualityCheckerTool {
  name: "validateQuality";
  description: "Validate investigation report quality and approve completion";
  
  parameters: {
    investigation_report: InvestigationReport;
    quality_threshold?: number;      // Minimum quality score for approval
    validation_depth?: 'basic' | 'comprehensive';
  };
  
  response: {
    success: boolean;
    quality_score: number;          // Overall quality 0.0 to 1.0
    validation_details: {           // Detailed quality breakdown
      completeness: number;
      evidence_quality: number;
      regulatory_accuracy: number; 
      readability: number;
    };
    approved: boolean;              // Report approved for completion
    complete: boolean;              // Validation process complete
    improvement_suggestions: string[]; // Specific improvement recommendations
    error?: string;
    execution_time: number;
  };
}
```

---

**Document Status:** ✅ Ready for Ralph Implementation  
**Last Updated:** January 2026  
**Next Review:** March 2026  
**Maintainer:** Engineering Team  
**Approval:** Technical Lead, Product Owner, Security Team