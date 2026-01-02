# CardioGuard AI - Quick Start Guide

## Prerequisites
- Python 3.11+ installed
- API keys for:
  - Anthropic (Claude API)
  - Pinecone (optional, for vector storage)

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# Copy from .env.template if available, or create manually
ANTHROPIC_API_KEY=your_claude_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
```

### 3. Launch Application
```bash
streamlit run app.py
```

### 4. Access the Interface
Open your browser to: `http://localhost:8501`

## Usage

1. **Enter Provider NPI**: Input a 10-digit National Provider Identifier
2. **Click "Analyze Provider"**: System will collect data and analyze fraud risk
3. **Review Results**: 
   - Risk score (0-100)
   - Evidence summary
   - Recommendations
   - Regulatory citations
4. **Export Report**: Download PDF investigation report

## File Structure

```
CardioGuard_AI/
├── app.py              # Streamlit UI (main entry point)
├── workflow.py         # Workflow orchestration
├── config.py           # Configuration management
├── models.py           # Data models
├── agents/             # Multi-agent system
│   ├── research_agent.py
│   ├── pattern_analyzer.py
│   ├── report_writer.py
│   └── quality_checker.py
├── services/           # Data services
│   ├── cms_service.py
│   ├── oig_service.py
│   ├── nppes_service.py
│   └── export_service.py
└── docs/               # Documentation
```

## Troubleshooting

### Configuration Errors
- Ensure `.env` file exists with valid API keys
- Check that all required environment variables are set

### API Errors
- Verify API keys are correct
- Check API rate limits
- Ensure internet connection for data source APIs

### Import Errors
- Ensure you're running from project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

## Next Steps

- Review `docs/` folder for detailed documentation
- Check `status_summaries.md` for development progress
- Run tests: `pytest tests/`

## Support

For detailed information, see:
- `docs/README_CardioGuard_AI.md` - Project overview
- `docs/TECH_REQUIREMENTS.md` - Technical specifications
- `docs/BUILD_PLAN_1DAY.md` - Development plan
