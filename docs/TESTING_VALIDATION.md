# Testing & Validation Guide - CardioGuard_AI

## 🎯 Testing Objective
Validate fraud detection accuracy and system performance with minimal token usage during development.

## 📊 Test Data Strategy

### Known Test Cases
```json
{
  "fraud_case_high_risk": {
    "npi": "1234567890",
    "description": "Simulated cardiology upcoding scheme",
    "expected_risk_score": "80-100",
    "expected_priority": "high",
    "fraud_indicators": [
      "billing_volume_anomaly",
      "temporal_clustering", 
      "peer_deviation_high"
    ],
    "test_purpose": "Validate high-risk fraud detection"
  },
  "normal_provider": {
    "npi": "0987654321", 
    "description": "Normal cardiology practice baseline",
    "expected_risk_score": "0-30",
    "expected_priority": "low",
    "fraud_indicators": [],
    "test_purpose": "Validate false positive prevention"
  },
  "medium_risk_case": {
    "npi": "1122334455",
    "description": "Minor billing irregularities",
    "expected_risk_score": "40-60",
    "expected_priority": "medium", 
    "fraud_indicators": ["minor_peer_deviation"],
    "test_purpose": "Validate nuanced risk assessment"
  }
}
```

## 🧪 Component Testing

### 1. Research Agent Validation
```python
# Test: Data collection functionality
def test_research_agent():
    """Validate Research Agent data collection."""
    from agents.research_agent import ResearchAgent
    
    agent = ResearchAgent()
    
    # Test CMS data collection
    cms_result = await agent.get_cms_data("1234567890")
    assert "total_services" in cms_result
    assert "unique_beneficiaries" in cms_result
    
    # Test OIG exclusion check
    oig_result = await agent.check_oig_exclusion("1234567890") 
    assert "excluded" in oig_result
    
    # Test NPPES data
    nppes_result = await agent.get_provider_details("1234567890")
    assert "npi" in nppes_result
    
    print("✅ Research Agent: All data sources working")

# Expected Results:
# - CMS API returns provider utilization data
# - OIG check returns exclusion status
# - NPPES returns provider credentials
# - Processing time <15 seconds
```

### 2. Pattern Analyzer Validation
```python
# Test: Fraud detection algorithms
def test_pattern_analyzer():
    """Validate fraud pattern detection accuracy."""
    from agents.pattern_analyzer import PatternAnalyzer
    
    analyzer = PatternAnalyzer()
    
    # Test statistical anomaly detection
    test_provider = {
        "total_services": 5000,  # Very high
        "unique_beneficiaries": 100,  # Low ratio
        "total_charges": 2000000  # Very high
    }
    
    peer_baseline = {
        "total_services": {"mean": 1000, "std": 200},
        "unique_beneficiaries": {"mean": 300, "std": 50},
        "total_charges": {"mean": 500000, "std": 100000}
    }
    
    anomalies = analyzer.detect_statistical_anomalies(test_provider, peer_baseline)
    
    assert anomalies["total_services"]["z_score"] > 2.5
    assert anomalies["unique_beneficiaries"]["z_score"] < -2.5
    
    risk_score = analyzer.calculate_risk_score(anomalies)
    assert risk_score > 70  # Should be high risk
    
    print(f"✅ Pattern Analyzer: Risk score {risk_score}/100")

# Expected Results:
# - High volume, low beneficiary count triggers anomaly
# - Z-scores properly calculated vs baseline
# - Risk score >70 for suspicious patterns
# - Processing time <10 seconds
```

### 3. Report Writer Validation
```python
# Test: Investigation report generation
def test_report_writer():
    """Validate report generation quality."""
    from agents.report_writer import ReportWriter
    
    writer = ReportWriter()
    
    test_analysis = {
        "provider_npi": "1234567890",
        "risk_score": 85,
        "anomalies": [
            {"type": "billing_volume", "severity": "high"},
            {"type": "temporal_clustering", "severity": "medium"}
        ],
        "evidence": ["340% above peer average", "End-of-month clustering"]
    }
    
    report = await writer.generate_investigation_report(test_analysis)
    
    # Validate report structure
    assert "EXECUTIVE SUMMARY" in report.content
    assert "EVIDENCE ANALYSIS" in report.content  
    assert "RECOMMENDATIONS" in report.content
    assert report.risk_score == 85
    assert report.priority == "high"
    
    print("✅ Report Writer: Professional report generated")

# Expected Results:
# - Report contains all required sections
# - Evidence properly summarized
# - Recommendations are actionable
# - Professional formatting suitable for compliance
# - Processing time <10 seconds
```

### 4. UI Integration Testing
```python
# Test: Streamlit interface functionality
def test_streamlit_ui():
    """Manual test of Streamlit interface."""
    
    # Launch application
    # streamlit run app.py
    
    # Manual validation steps:
    # 1. Open http://localhost:8501
    # 2. Enter test NPI: 1234567890
    # 3. Click "Analyze Provider" 
    # 4. Verify results display within 30 seconds
    # 5. Check risk score is 80-100 (high)
    # 6. Verify evidence summary shows anomalies
    # 7. Test PDF export functionality
    
    validation_checklist = [
        "UI loads without errors",
        "Provider input field accepts NPI",
        "Analysis button triggers processing",
        "Progress indicator shows during analysis",
        "Results display risk score and evidence",
        "PDF export generates downloadable report",
        "Processing completes in <30 seconds"
    ]
    
    return validation_checklist

# Manual verification required for UI testing
```

## 🎯 End-to-End Validation

### Complete Workflow Test
```python
async def test_complete_workflow():
    """Test full fraud investigation workflow."""
    
    # Test Case 1: Known Fraud Pattern
    print("Testing known fraud case...")
    result_fraud = await run_fraud_investigation("1234567890")
    
    assert result_fraud["risk_score"] >= 80
    assert result_fraud["priority"] == "high"
    assert len(result_fraud["evidence"]) >= 2
    print(f"✅ Fraud Case: Risk {result_fraud['risk_score']}/100")
    
    # Test Case 2: Normal Provider
    print("Testing normal provider...")
    result_normal = await run_fraud_investigation("0987654321")
    
    assert result_normal["risk_score"] <= 30
    assert result_normal["priority"] == "low"
    print(f"✅ Normal Case: Risk {result_normal['risk_score']}/100")
    
    # Test Case 3: Performance Validation
    import time
    start_time = time.time()
    result_performance = await run_fraud_investigation("1122334455")
    processing_time = time.time() - start_time
    
    assert processing_time < 30  # Under 30 seconds
    print(f"✅ Performance: {processing_time:.1f} seconds")

# Expected Results:
# - Fraud case: Risk score 80-100
# - Normal case: Risk score 0-30  
# - Processing time: <30 seconds
# - No system errors or exceptions
```

### Accuracy Validation
```python
def validate_fraud_detection_accuracy():
    """Validate overall system accuracy."""
    
    test_cases = [
        {"npi": "1234567890", "expected": "high", "description": "Fraud case"},
        {"npi": "0987654321", "expected": "low", "description": "Normal provider"},
        {"npi": "1122334455", "expected": "medium", "description": "Minor issues"}
    ]
    
    correct_predictions = 0
    total_cases = len(test_cases)
    
    for case in test_cases:
        result = run_fraud_investigation(case["npi"])
        predicted_priority = result["priority"]
        
        if predicted_priority == case["expected"]:
            correct_predictions += 1
            print(f"✅ {case['description']}: Correct prediction ({predicted_priority})")
        else:
            print(f"❌ {case['description']}: Expected {case['expected']}, got {predicted_priority}")
    
    accuracy = (correct_predictions / total_cases) * 100
    print(f"\n📊 Overall Accuracy: {accuracy:.1f}%")
    
    assert accuracy >= 90  # 90% accuracy requirement
    return accuracy

# Target: >90% accuracy on validation cases
```

## 💰 Cost Validation

### API Usage Monitoring
```python
class CostTracker:
    def __init__(self):
        self.api_calls = []
        self.total_cost = 0.0
        
    def track_api_call(self, service: str, tokens: int, cost: float):
        """Track individual API calls and costs."""
        self.api_calls.append({
            "service": service,
            "tokens": tokens, 
            "cost": cost,
            "timestamp": datetime.now()
        })
        self.total_cost += cost
        
    def get_cost_summary(self) -> dict:
        """Get cost breakdown summary."""
        claude_calls = [call for call in self.api_calls if call["service"] == "claude"]
        total_claude_tokens = sum(call["tokens"] for call in claude_calls)
        total_claude_cost = sum(call["cost"] for call in claude_calls)
        
        return {
            "total_investigations": len(self.api_calls),
            "total_cost": self.total_cost,
            "cost_per_investigation": self.total_cost / max(len(self.api_calls), 1),
            "claude_tokens": total_claude_tokens,
            "claude_cost": total_claude_cost,
            "monthly_projection": self.total_cost * 30  # Assuming daily usage
        }

# Target: <$5/month total cost
# Expected: ~$0.10-0.50 per investigation
```

## 📋 Validation Checklist

### Pre-Deployment Validation
- [ ] **Research Agent** collects data from all sources
- [ ] **Pattern Analyzer** detects known fraud patterns
- [ ] **Report Writer** generates professional reports
- [ ] **UI Interface** allows complete investigation workflow
- [ ] **PDF Export** creates downloadable investigation reports

### Accuracy Validation
- [ ] **High-risk case** scored 80-100 with evidence
- [ ] **Normal case** scored 0-30 without false positives  
- [ ] **Medium-risk case** scored 40-60 with appropriate evidence
- [ ] **Processing time** consistently under 30 seconds
- [ ] **Report quality** suitable for compliance review

### Cost Validation
- [ ] **API costs** under $0.50 per investigation
- [ ] **Monthly projection** under $5.00 total
- [ ] **Token usage** optimized for efficiency
- [ ] **Free tier limits** respected (Pinecone)

### User Experience Validation
- [ ] **Interface** intuitive for fraud investigators
- [ ] **Error handling** provides helpful messages
- [ ] **Results** clearly formatted and actionable
- [ ] **Export** generates professional PDF reports
- [ ] **Performance** meets daily usage requirements

## 🚀 Success Criteria

### System is Ready When:
1. ✅ All component tests pass
2. ✅ End-to-end workflow completes successfully  
3. ✅ Known fraud cases detected accurately (>90%)
4. ✅ Normal providers don't trigger false positives (<5%)
5. ✅ Processing time meets 30-second requirement
6. ✅ Cost stays within $5/month budget
7. ✅ PDF reports export with proper formatting
8. ✅ Interface ready for daily FI use

### Quality Metrics Target
- **Detection Accuracy:** >90% on known cases
- **False Positive Rate:** <5% on normal providers  
- **Processing Speed:** <30 seconds per analysis
- **Cost Efficiency:** <$0.50 per investigation
- **Report Quality:** Professional standard for compliance
- **User Satisfaction:** Single-page workflow completion

---

*This testing guide ensures fraud detection accuracy and system reliability with efficient validation procedures.*
