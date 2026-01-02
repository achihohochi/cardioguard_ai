# Agent Architecture Guide - CardioGuard_AI

## 🎯 Purpose
Reference document for multi-agent architecture patterns to minimize token usage during development.

## 🏗️ Multi-Agent Framework Overview

### Agent Communication Flow
```
Provider NPI Input
    ↓
Research Agent (Data Collection)
    ↓
Pattern Analyzer (Fraud Detection)
    ↓
Report Writer (Investigation Report)
    ↓
Quality Checker (Validation)
    ↓
Investigation Report Output
```

## 🤖 Agent Specifications

### 1. Research Agent
**File:** `agents/research_agent.py`
**Purpose:** Multi-source healthcare data collection and provider profiling

#### Core Functions:
```python
async def collect_provider_intelligence(npi: str) -> ProviderProfile:
    # Primary function for data collection
    
async def get_cms_utilization_data(npi: str) -> dict:
    # CMS provider utilization patterns
    
async def check_oig_exclusion_status(npi: str) -> dict:
    # OIG exclusion database check
    
async def get_provider_credentials(npi: str) -> dict:
    # NPPES registry data
    
def fuse_data_sources(cms_data: dict, oig_data: dict, nppes_data: dict) -> ProviderProfile:
    # Combine multiple data sources into unified profile
```

#### Key Patterns:
- **Parallel Data Collection:** Simultaneous API calls to multiple sources
- **Error Handling:** Graceful degradation when data sources unavailable
- **Data Fusion:** Combine disparate data into unified provider profile
- **Caching Strategy:** Local storage for repeated queries

#### Dependencies:
- `requests` for API calls
- `asyncio` for parallel processing
- `pandas` for data manipulation
- Local caching mechanism

---

### 2. Pattern Analyzer
**File:** `agents/pattern_analyzer.py`
**Purpose:** Fraud pattern detection and statistical analysis

#### Core Functions:
```python
def analyze_fraud_patterns(provider: ProviderProfile) -> dict:
    # Main analysis orchestration
    
def calculate_statistical_anomalies(provider: ProviderProfile, peer_data: list) -> dict:
    # Z-score analysis vs peer baselines
    
def detect_temporal_patterns(billing_data: list) -> dict:
    # End-of-month clustering, volume spikes
    
def analyze_geographic_patterns(provider: ProviderProfile) -> dict:
    # Service area vs patient distribution analysis
    
def calculate_risk_score(anomalies: dict) -> int:
    # 0-100 risk score calculation
```

#### Key Algorithms:
- **Statistical Analysis:** Z-score calculation for billing anomalies
- **Temporal Analysis:** Time-series pattern detection
- **Geographic Analysis:** Service area concentration detection
- **Risk Scoring:** Weighted composite scoring (0-100 scale)

#### Dependencies:
- `numpy` for numerical calculations
- `scipy` for statistical functions
- `sklearn` for pattern detection
- Custom fraud detection algorithms

---

### 3. Report Writer
**File:** `agents/report_writer.py`
**Purpose:** Investigation report generation with LLM assistance

#### Core Functions:
```python
async def generate_investigation_report(analysis_results: dict) -> InvestigationReport:
    # Main report generation orchestration
    
async def create_executive_summary(risk_score: int, key_findings: list) -> str:
    # High-level summary for leadership
    
async def generate_evidence_section(anomalies: dict) -> str:
    # Detailed evidence analysis
    
async def create_recommendations(risk_score: int, evidence: list) -> list:
    # Actionable investigation steps
    
def format_report_for_export(report_content: str) -> InvestigationReport:
    # Professional formatting for PDF export
```

#### LLM Integration:
- **Claude Haiku:** Cost-optimized model for report generation
- **Prompt Templates:** Standardized prompts for consistent output
- **Token Optimization:** Minimal context, focused prompts
- **Quality Control:** Automated content validation

#### Dependencies:
- `anthropic` for Claude API integration
- Custom prompt templates
- Report formatting utilities
- PDF generation libraries

---

### 4. Quality Checker
**File:** `agents/quality_checker.py`
**Purpose:** Report validation and quality assurance

#### Core Functions:
```python
def validate_report_quality(report: InvestigationReport) -> bool:
    # Main validation orchestration
    
def check_completeness(report: InvestigationReport) -> dict:
    # Verify all required sections present
    
def validate_evidence_accuracy(evidence: list) -> dict:
    # Check evidence relevance and accuracy
    
def verify_regulatory_compliance(report: InvestigationReport) -> dict:
    # Ensure proper citations and compliance
    
def calculate_quality_score(validation_results: dict) -> float:
    # Overall quality assessment (0.0-1.0)
```

#### Quality Metrics:
- **Completeness:** All required sections present
- **Accuracy:** Evidence supports conclusions
- **Compliance:** Proper regulatory citations
- **Professional Standards:** Suitable for compliance review

#### Dependencies:
- Validation rule engine
- Regulatory citation database
- Quality scoring algorithms
- Error reporting utilities

## 🔄 Agent Coordination Patterns

### Workflow Orchestration
```python
class FraudInvestigationWorkflow:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.pattern_analyzer = PatternAnalyzer()
        self.report_writer = ReportWriter()
        self.quality_checker = QualityChecker()
    
    async def run_investigation(self, npi: str) -> InvestigationReport:
        # Step 1: Data Collection
        provider_profile = await self.research_agent.collect_provider_intelligence(npi)
        
        # Step 2: Pattern Analysis
        analysis_results = self.pattern_analyzer.analyze_fraud_patterns(provider_profile)
        
        # Step 3: Report Generation
        draft_report = await self.report_writer.generate_investigation_report(analysis_results)
        
        # Step 4: Quality Validation
        if self.quality_checker.validate_report_quality(draft_report):
            return draft_report
        else:
            # Handle quality issues and retry if needed
            return self.handle_quality_issues(draft_report)
```

### Error Handling Strategy
- **Graceful Degradation:** Continue with partial data when sources unavailable
- **Retry Logic:** Automatic retry for transient failures
- **Fallback Mechanisms:** Alternative data sources when primary fails
- **User Communication:** Clear error messages for investigation team

### Performance Optimization
- **Caching:** Store frequently accessed data locally
- **Parallel Processing:** Simultaneous execution where possible
- **Resource Management:** Efficient memory and CPU usage
- **Cost Control:** Monitor API usage and optimize calls

## 📊 Data Flow Architecture

### Input Processing
```
Provider NPI → Validation → Data Collection Request → Multi-Source APIs
```

### Analysis Pipeline
```
Raw Data → Data Fusion → Statistical Analysis → Pattern Detection → Risk Scoring
```

### Output Generation
```
Analysis Results → Report Template → LLM Enhancement → Quality Check → Final Report
```

## 🎯 Development Guidelines

### Code Organization
- **Single Responsibility:** Each agent has one primary purpose
- **Loose Coupling:** Agents communicate through well-defined interfaces
- **Error Isolation:** Agent failures don't cascade to other components
- **Testability:** Each agent can be tested independently

### Performance Targets
- **Research Agent:** <15 seconds for data collection
- **Pattern Analyzer:** <10 seconds for analysis
- **Report Writer:** <10 seconds for generation
- **Quality Checker:** <5 seconds for validation
- **Total Workflow:** <30 seconds end-to-end

### Token Efficiency
- **Focused Prompts:** Specific, minimal context for LLM calls
- **Batch Processing:** Combine multiple operations when possible
- **Caching:** Reuse LLM responses for similar queries
- **Model Selection:** Use Claude Haiku for cost optimization

## 🔧 Implementation Notes

### Agent Base Class
```python
class BaseAgent:
    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logging()
        self.cache = setup_caching()
    
    async def execute(self, input_data: dict) -> dict:
        # Template method pattern for consistent execution
        
    def handle_error(self, error: Exception) -> dict:
        # Standardized error handling
        
    def log_activity(self, action: str, data: dict):
        # Consistent logging across agents
```

### Configuration Management
- **Environment Variables:** API keys and settings
- **Config Files:** Agent-specific parameters
- **Runtime Configuration:** Dynamic settings adjustment
- **Validation:** Configuration correctness checking

---

*This guide provides the architectural foundation for efficient agent development with minimal token usage.*
