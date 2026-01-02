# 🏥 CardioGuard AI - Healthcare Fraud Detection

**Fast, accurate fraud risk analysis for healthcare providers**

CardioGuard AI helps fraud investigators quickly identify healthcare providers with suspicious billing patterns. Get a complete fraud risk assessment in under 30 seconds.

---

## What Does It Do?

CardioGuard AI analyzes healthcare providers to detect potential fraud by:

1. **Collecting Data** from multiple government sources:
   - CMS (Medicare billing patterns)
   - OIG (exclusion and sanction database)
   - NPPES (provider credentials and information)

2. **Analyzing Patterns** to find:
   - Unusual billing volumes compared to similar providers
   - Suspicious billing patterns (like end-of-month clustering)
   - Providers on exclusion lists
   - Other fraud indicators

3. **Generating Reports** with:
   - Risk score (0-100)
   - Evidence summary
   - Actionable recommendations
   - Regulatory citations

---

## Key Features

✅ **Fast Analysis** - Complete investigation in ~30 seconds  
✅ **Comprehensive Data** - Pulls from CMS, OIG, and NPPES databases  
✅ **Risk Scoring** - Clear 0-100 risk score with color coding  
✅ **Evidence-Based** - Detailed findings with statistical significance  
✅ **Professional Reports** - Export PDF reports for compliance teams  
✅ **Cost-Effective** - Uses free public APIs, minimal operating costs  

---

## How to Use

### Step 1: Setup (One-Time)

1. **Install Python** (3.11 or higher)
   - Download from [python.org](https://www.python.org/downloads/)

2. **Get API Keys**
   - **Anthropic API Key** (required): Get from [console.anthropic.com](https://console.anthropic.com/)
   - **Pinecone API Key** (optional): Get from [pinecone.io](https://www.pinecone.io/)

3. **Install Dependencies**
   ```bash
   cd CardioGuard_AI
   source venv/bin/activate  # Activate virtual environment
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     ANTHROPIC_API_KEY=your_key_here
     PINECONE_API_KEY=your_key_here  # Optional
     PINECONE_ENVIRONMENT=your_environment  # Optional
     ```

### Step 2: Launch the App

```bash
cd CardioGuard_AI
source venv/bin/activate
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Step 3: Analyze a Provider

1. **Enter Provider NPI**
   - Find NPIs at [NPPES Registry](https://npiregistry.cms.hhs.gov/)
   - Enter the 10-digit NPI number

2. **Click "Analyze Provider"**
   - Wait ~30 seconds for analysis
   - Progress indicator shows what's happening

3. **Review Results**
   - **Risk Score**: Color-coded (🟢 Low / 🟡 Medium / 🔴 High)
   - **Executive Summary**: High-level overview
   - **Evidence**: Detailed findings with severity levels
   - **Recommendations**: Next steps for investigation

4. **Export Report**
   - Click "Download PDF Report"
   - Professional report ready for compliance teams

---

## Understanding Risk Scores

| Score Range | Priority | Meaning | Action |
|------------|----------|---------|--------|
| **0-29** | 🟢 Low | Normal billing patterns | Routine monitoring |
| **30-69** | 🟡 Medium | Some anomalies detected | Further review recommended |
| **70-100** | 🔴 High | Multiple fraud indicators | Immediate investigation |

---

## What Data Sources Are Used?

### CMS Open Data
- Provider billing and utilization patterns
- Service volumes and charges
- Medicare participation status

### OIG Exclusion Database
- Providers excluded from Medicare/Medicaid
- Enforcement actions and sanctions
- Exclusion types and dates

### NPPES Registry
- Provider credentials and licenses
- Practice locations
- Specialty information

**All data sources are free and publicly available.**

---

## Example Output

When you analyze a provider, you'll see:

**Risk Score: 85/100 (High Risk)** 🔴

**Executive Summary:**
> This investigation report analyzes the fraud risk profile of Dr. John Smith (NPI: 1234567890). The analysis indicates a high risk level with a risk score of 85/100. Key findings include billing volume anomalies 340% above peer average and end-of-month billing clustering patterns...

**Evidence:**
1. **Billing Anomaly - Total Services**: Services per beneficiary is high (Z-score: 3.2, Value: 15.5)
   - Severity: HIGH | Source: CMS

2. **OIG Exclusion**: Provider is excluded from Medicare/Medicaid: Mandatory - Medicare/Medicaid conviction
   - Severity: HIGH | Source: OIG

**Recommendations:**
1. Prioritize for immediate investigation due to high risk score
2. Review detailed billing records for the past 12 months
3. Conduct provider interview to address identified anomalies

---

## Troubleshooting

### "Configuration Error" Message
- Make sure your `.env` file exists in the project root
- Verify `ANTHROPIC_API_KEY` is set correctly
- Restart the Streamlit app after updating `.env`

### "Module not found" Errors
- Activate your virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Analysis Takes Too Long
- First run may take longer (~60 seconds) while downloading OIG data
- Subsequent runs use cached data and are faster (~30 seconds)
- Check your internet connection

### No Results Found
- Verify the NPI is correct (must be exactly 10 digits)
- Some providers may have limited data in public databases
- Try a different NPI from the NPPES registry

---

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Windows, or Linux
- **Internet Connection**: Required for API access
- **Memory**: 2GB RAM minimum
- **Storage**: ~500MB for application and cache

---

## Cost Information

- **Development**: Free (open source)
- **Monthly Operating Cost**: <$5 (Claude API usage)
- **Data Sources**: 100% free (public APIs)
- **Infrastructure**: Free (runs locally)

**Estimated cost per investigation**: ~$0.01-0.05

---

## Getting Help

- **Quick Start Guide**: See `QUICKSTART.md`
- **Run Guide**: See `RUN_GUIDE.md`
- **Detailed Documentation**: See `docs/` folder
- **Status Updates**: See `status_summaries.md`

---

## Privacy & Security

- **No PHI Processing**: Only uses publicly available data
- **Local Processing**: All analysis runs on your machine
- **API Keys**: Stored securely in `.env` file (never committed to git)
- **Data Caching**: Downloaded data cached locally for performance

---

## License

MIT License - Commercial use permitted for healthcare fraud detection applications.

---

**Built for healthcare fraud investigators who need fast, accurate, and actionable intelligence.**

*Transform healthcare fraud investigation from months to minutes.*
