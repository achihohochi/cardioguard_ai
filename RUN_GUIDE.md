# CardioGuard AI - Run & Test Guide

## Quick Start (3 Steps)

### Step 1: Activate Virtual Environment
```bash
cd /Users/chiho/ai-lab/CardioGuard_AI
source venv/bin/activate
```

### Step 2: Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys
Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_claude_api_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=cardioguard-vectors
PREFERRED_MODEL=claude-3-haiku-20240307
MAX_MONTHLY_API_COST=5.00
MAX_TOKENS_PER_REQUEST=1000
LOG_LEVEL=INFO
EOF
```

**Important:** Replace `your_claude_api_key_here` with your actual Anthropic API key. Pinecone is optional but recommended.

### Step 4: Launch the Application
```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## Testing Functionality

### Test Case 1: Valid NPI (Real Provider)
1. **Enter a real NPI**: Use a 10-digit NPI from NPPES registry
   - Example: `1234567890` (replace with actual NPI)
   - You can find real NPIs at: https://npiregistry.cms.hhs.gov/

2. **Click "Analyze Provider"**
   - System will collect data from CMS, OIG, and NPPES
   - Processing takes ~30 seconds
   - You'll see progress indicators

3. **Review Results**:
   - **Risk Score**: 0-100 (color-coded)
   - **Priority Level**: Low/Medium/High
   - **Executive Summary**: AI-generated summary
   - **Evidence Summary**: Detailed findings
   - **Recommendations**: Actionable next steps
   - **Regulatory Citations**: Relevant regulations

4. **Export PDF**: Click "Download PDF Report" button

### Test Case 2: Invalid NPI Format
1. Enter invalid NPI: `12345` (too short)
2. Click "Analyze Provider"
3. **Expected**: Error message "Invalid NPI format. Must be exactly 10 digits."

### Test Case 3: Missing API Keys
1. Remove or invalidate API keys in `.env`
2. Launch app: `streamlit run app.py`
3. **Expected**: Configuration error displayed in UI

---

## What to Expect

### Successful Analysis Flow:
```
1. Enter NPI → Click "Analyze Provider"
2. Progress spinner appears: "Analyzing provider fraud risk..."
3. System collects data (15-20 seconds):
   - CMS utilization data
   - OIG exclusion check
   - NPPES provider details
4. Pattern analysis (5 seconds):
   - Statistical anomalies
   - Risk score calculation
5. Report generation (5-10 seconds):
   - Executive summary (Claude Haiku)
   - Evidence compilation
   - Recommendations
6. Results displayed:
   - Risk score with color coding
   - All sections populated
   - PDF download available
```

### Expected Output Sections:
- ✅ **Risk Score**: Number between 0-100
- ✅ **Priority Level**: Low, Medium, or High
- ✅ **Executive Summary**: 2-3 paragraph summary
- ✅ **Evidence Summary**: List of fraud indicators
- ✅ **Recommendations**: Actionable investigation steps
- ✅ **Regulatory Citations**: List of relevant regulations

---

## Troubleshooting

### Issue: "Configuration Error" on startup
**Solution**: 
- Check `.env` file exists in project root
- Verify `ANTHROPIC_API_KEY` is set
- Restart Streamlit app

### Issue: "Module not found" errors
**Solution**:
```bash
# Ensure you're in the project directory
cd /Users/chiho/ai-lab/CardioGuard_AI

# Activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API errors during analysis
**Solution**:
- Verify API keys are correct
- Check internet connection
- Some APIs may have rate limits - wait a few minutes and retry

### Issue: Analysis takes too long (>60 seconds)
**Solution**:
- Check internet connection
- Some data sources may be slow
- Check logs in terminal for specific errors

### Issue: PDF export fails
**Solution**:
- Ensure `reportlab` is installed: `pip install reportlab`
- Check that `data/reports/` directory exists (created automatically)

---

## Testing with Sample NPIs

### Finding Real NPIs for Testing:
1. Visit: https://npiregistry.cms.hhs.gov/
2. Search for providers by name or location
3. Copy a 10-digit NPI
4. Use in the app

### Example Test Scenarios:

**Scenario A: High-Risk Provider**
- Look for providers with:
  - High billing volumes
  - Multiple service types
  - Recent OIG exclusions (if any)

**Scenario B: Low-Risk Provider**
- Look for providers with:
  - Normal billing patterns
  - Single specialty
  - No exclusions

---

## Monitoring & Logs

### View Logs:
Logs are displayed in the terminal where you ran `streamlit run app.py`

### Log Levels:
- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Errors that need attention

### Cache Locations:
- CMS data: `data/cache/cms/`
- OIG data: `data/cache/oig_exclusions.csv`
- NPPES data: `data/cache/nppes/`
- Reports: `data/reports/`

---

## Performance Benchmarks

### Expected Performance:
- **Data Collection**: 15-20 seconds
- **Pattern Analysis**: 5 seconds
- **Report Generation**: 5-10 seconds
- **Total Time**: <30 seconds

### Cost Per Analysis:
- Claude Haiku API: ~$0.01-0.05 per analysis
- Target: <$0.50 per investigation
- Monthly budget: <$5 for 100+ investigations

---

## Next Steps After Testing

1. **Review Results**: Check if risk scores make sense
2. **Validate Evidence**: Verify evidence is relevant
3. **Test PDF Export**: Download and review PDF reports
4. **Performance Check**: Ensure analysis completes in <30 seconds
5. **Cost Monitoring**: Track API usage to stay under budget

---

## Getting Help

- **Documentation**: See `docs/` folder
- **Status**: Check `status_summaries.md`
- **Issues**: Review terminal logs for error details
