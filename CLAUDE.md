# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CardioGuard AI is a healthcare fraud detection system that analyzes providers for suspicious billing patterns using government APIs (CMS, OIG, NPPES) and web search. Built with Streamlit, it provides fraud investigators with risk scores and investigation reports in under 30 seconds.

## Development Commands

### Starting the Application
```bash
# Activate virtual environment and run Streamlit app
source venv/bin/activate
streamlit run app.py
```

### Testing
```bash
# Run test suite (uses pytest)
pytest tests/
pytest tests/test_workflow.py  # Run specific test file
```

### Dependency Management
```bash
pip install -r requirements.txt
```

### Environment Setup
Create `.env` file with:
```
ANTHROPIC_API_KEY=your_claude_key_here
PINECONE_API_KEY=your_pinecone_key_here  # Optional
PINECONE_ENVIRONMENT=your_environment    # Optional
```

## Architecture Overview

### Multi-Agent System
The application uses a 4-agent pipeline orchestrated by `workflow.py`:

1. **Research Agent** (`agents/research_agent.py`) - Data collection from CMS, OIG, NPPES, and web search
2. **Pattern Analyzer** (`agents/pattern_analyzer.py`) - Statistical fraud detection using scipy/sklearn
3. **Report Writer** (`agents/report_writer.py`) - LLM-powered report generation using Anthropic Claude
4. **Quality Checker** (`agents/quality_checker.py`) - Report validation and quality assurance

### Key Components

- **Main Entry Point**: `app.py` - Streamlit UI with provider NPI input and fraud analysis results
- **Workflow Orchestration**: `workflow.py` - Coordinates all agents in sequence
- **Data Models**: `models.py` - Pydantic models for type safety (ProviderProfile, InvestigationReport, etc.)
- **Configuration**: `config.py` - Environment variables, API settings, cache configuration

### Service Layer (`services/`)
- `data_service.py` - Main data collection coordinator
- `cms_service.py` - CMS Open Data API integration
- `oig_service.py` - OIG Exclusion Database processing
- `nppes_service.py` - NPPES Registry API
- `web_search_service.py` - DuckDuckGo search for legal information
- `export_service.py` - PDF report generation

### Data Flow
```
Provider NPI → Research Agent (parallel data collection) → Pattern Analyzer (fraud detection) → Report Writer (LLM report) → Quality Checker → Investigation Report
```

## Development Patterns

### Async/Await Usage
The system heavily uses async/await for parallel data collection. Key files:
- `workflow.py` - Main async orchestration
- `agents/research_agent.py` - Parallel API calls to multiple sources
- `services/data_service.py` - Concurrent data fetching

### Error Handling Strategy
- Graceful degradation when data sources are unavailable
- Continue with partial data rather than failing completely
- Log errors but don't break the workflow
- Clear user feedback in Streamlit UI

### Caching Implementation
- Local file caching in `data/cache/` directory
- Different cache durations per data source (CMS: 24h, OIG: 30 days, NPPES: 7 days)
- Cache keys based on provider NPI and data source

### Cost Control
- Uses Claude Haiku model for cost optimization
- Token limits configured in `config.py`
- Monthly cost tracking (target <$5/month)

## Key Files for Development

- `app.py` - Modify UI components, add new features to Streamlit interface
- `workflow.py` - Add new agents or modify the investigation pipeline
- `agents/pattern_analyzer.py` - Implement new fraud detection algorithms
- `agents/report_writer.py` - Modify LLM prompts and report generation
- `services/` - Add new data sources or modify existing API integrations
- `models.py` - Add new data structures or modify existing ones

## Data Sources and APIs

- **CMS Open Data**: Provider utilization and billing patterns (free)
- **OIG Exclusions**: Provider sanctions and exclusions (free CSV download)
- **NPPES Registry**: Provider credentials and information (free API)
- **DuckDuckGo Search**: Legal and court records (free search)

All data sources are free public APIs with no authentication required except for the Anthropic Claude API.

## Deployment

Configured for Render deployment via `render.yaml`:
- Python 3.11 runtime specified in `runtime.txt`
- Environment variables configured for production
- Streamlit server configured for headless operation

## Performance Targets

- Total analysis time: <30 seconds
- Research Agent: <15 seconds
- Pattern Analyzer: <10 seconds  
- Report generation: <10 seconds
- Quality check: <5 seconds