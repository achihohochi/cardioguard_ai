# PROJECT_STATE — CardioGuard_AI

Last updated: 2025-01-02
Owner: chiho
Current branch: main
Last known good commit: a3d88e3 (Add web search legal information feature and fix async data collection bug)

## 0) TL;DR (60 seconds)
**What this repo does:** Healthcare fraud detection system that analyzes provider NPIs to generate fraud risk scores (0-100) with evidence-based investigation reports in ~30 seconds using CMS, OIG, NPPES, and web search (legal/court records) data sources.

**Phase 1 goal:** Complete working fraud detection system with multi-agent architecture, Streamlit UI, and PDF report generation. System must correctly identify excluded providers (especially felony convictions) with risk scores 90+.

**Phase 1 status:** ✅ Complete (with recent bug fixes applied)

**Phase 2 goal:** Full end-to-end testing, performance optimization, cost monitoring, and user acceptance testing with real-world fraud cases.

## 1) Current "Definition of Done"

### Phase 1 (baseline) ✅
- ✅ Multi-agent architecture (Research → Pattern Analyzer → Report Writer → Quality Checker)
- ✅ CMS, OIG, NPPES API integrations with parallel data collection
- ✅ Web search integration for legal/court records (DuckDuckGo, free tier)
- ✅ Risk scoring algorithm with OIG exclusion prioritization (felony = 90+, mandatory = 80+, permissive = 70+)
- ✅ Legal information risk scoring (convictions +20, pending lawsuits +15, allegations +10)
- ✅ Streamlit UI for provider NPI input and results display
- ✅ Data sources status display (CMS, OIG, NPPES, Web Search)
- ✅ Evidence summary with clickable URLs for web search sources
- ✅ PDF report generation with evidence summaries and recommendations
- ✅ CMS API endpoint fixed (using correct CMS Open Data API v1)
- ✅ Risk scoring correctly identifies excluded providers (tested with NPI 1992796015)
- ✅ CMS failures handled gracefully (system works with OIG + NPPES alone)
- ✅ Async data collection bug fixed (variable name mismatch resolved)
- ✅ Configuration management with .env file
- ✅ .gitignore protecting sensitive API keys

### Phase 2 (next) 🟡
- 🟡 Full end-to-end testing with multiple real NPIs (high-risk and low-risk cases)
- 🟡 Performance validation (<30 seconds consistently)
- 🟡 Cost tracking and optimization (<$5/month target)
- 🟡 User acceptance testing with fraud investigators
- 🟡 Enhanced peer comparison baseline calculation
- 🟡 Advanced temporal pattern analysis with time-series data
- 🟡 Batch processing for multiple providers

## 2) What works right now (verified)

### Quick start (local)
**Prereqs:**
- OS: macOS (tested), Linux/Windows should work
- Python: 3.11+ (tested with 3.9)
- Other: Anthropic API key (required), Pinecone API key (optional)

**Setup:**
```bash
# 1) Activate virtual environment
cd /Users/chiho/ai-lab/CardioGuard_AI
source venv/bin/activate

# 2) Install dependencies (if needed)
pip install -r requirements.txt

# 3) Set environment variables
cp .env.template .env
# Fill values:
# - ANTHROPIC_API_KEY=your_claude_api_key (required)
# - PINECONE_API_KEY=your_pinecone_key (optional)
# - PINECONE_ENVIRONMENT=your_environment (optional)

# 4) Launch application
streamlit run app.py
# Opens at http://localhost:8501
```

**Test with known excluded provider:**
- NPI: `1992796015` (Scott Reuben, convicted felon)
- Expected: Risk score 90+ with HIGH priority
- Expected: OIG exclusion evidence with felony conviction details

### Verified functionality
- ✅ Provider NPI input validation (10 digits)
- ✅ Parallel data collection from CMS, OIG, NPPES, Web Search
- ✅ OIG exclusion detection (felony convictions, mandatory/permissive exclusions)
- ✅ Web search for legal/court records (convictions, lawsuits, allegations)
- ✅ Legal information parsing and relevance scoring
- ✅ Risk score calculation (0-100 scale) with legal information integration
- ✅ Evidence compilation with severity levels and source URLs
- ✅ Data sources status display in UI
- ✅ Executive summary generation (Claude Haiku)
- ✅ PDF report export
- ✅ Error handling for missing/invalid data
- ✅ CMS API failures handled gracefully (continues with OIG + NPPES)
- ✅ Web search failures handled gracefully (optional data source)

### Known limitations
- CMS API endpoint may need adjustment based on actual CMS API response format
- Peer baseline comparison uses default values (not real CMS peer data)
- Temporal pattern analysis is simplified (no time-series data available)
- Pinecone vector storage is optional and not fully integrated

## 3) Architecture overview

**Multi-Agent System:**
```
Provider NPI → Research Agent → Pattern Analyzer → Report Writer → Quality Checker → Investigation Report
```

**Data Flow:**
1. Research Agent collects from CMS, OIG, NPPES, Web Search (parallel async)
2. Pattern Analyzer detects anomalies, calculates risk score (includes legal information)
3. Report Writer generates executive summary and recommendations
4. Quality Checker validates report completeness
5. Export Service generates PDF report

**Key Files:**
- `app.py` - Streamlit UI entry point
- `workflow.py` - Agent orchestration
- `agents/` - 4 agent modules (research, pattern_analyzer, report_writer, quality_checker)
- `services/` - 8 service modules (CMS, OIG, NPPES, data, vector, export, web_search, legal_parser)
- `models.py` - Pydantic data models (includes LegalInformation)
- `config.py` - Configuration management

## 4) Recent changes

**2025-01-02: Web Search Legal Information Feature**
- Added WebSearchService for searching legal/court records (DuckDuckGo integration)
- Added LegalParserService to parse and classify legal information (convictions, lawsuits, allegations)
- Integrated web search into parallel data collection workflow
- Added LegalInformation model to ProviderProfile
- Updated risk scoring to include legal information (+20 convictions, +15 pending lawsuits, +10 allegations)
- Added legal evidence to FraudEvidence with source URLs
- Updated Streamlit UI to show web search in data sources
- Added data sources status display (CMS, OIG, NPPES, Web Search)
- Added clickable URL links in evidence summary for web search sources
- Made web search optional with graceful error handling
- Added web search configuration to config.py
- Added duckduckgo-search and beautifulsoup4 to requirements.txt
- Created test_web_search.py with basic tests

**2025-01-02: Critical Bug Fixes**
- Fixed async data collection bug (variable name mismatch: nppes_data_task vs nppes_task)
- Fixed CMS API endpoint (removed duplicate `/api/1/`, using correct CMS Open Data API v1)
- Fixed risk scoring algorithm to prioritize OIG exclusions (felony = 90+ mandatory)
- Made CMS optional (system works with OIG + NPPES alone)
- Enhanced error handling and logging

**2025-01-02: Documentation & Setup**
- Created PROJECT_STATE.md for project status tracking
- Created README.md for end users
- Created .gitignore to protect API keys
- Created QUICKSTART.md and RUN_GUIDE.md
- Added directory structure files (.gitkeep)

## 5) Testing status

**Unit Tests:** Basic structure in place (`tests/test_workflow.py`)
- NPI validation tests ✅
- End-to-end workflow tests 🟡 (requires API keys)

**Integration Tests:** Not yet implemented
- Real API testing with known providers
- Performance benchmarking
- Cost tracking validation

**Manual Testing:** ✅ Verified
- NPI 1992796015 (excluded provider) - Risk score 90+ ✅
- Streamlit UI launches and displays results ✅
- PDF export generates correctly ✅

## 6) Dependencies

**Core:**
- streamlit - UI framework
- anthropic - Claude API (Haiku model)
- pandas, numpy - Data processing
- pydantic - Data validation
- aiohttp - Async HTTP requests
- duckduckgo-search - Free web search (legal records)
- beautifulsoup4 - HTML parsing for search results

**Optional:**
- pinecone - Vector database (optional)
- reportlab - PDF generation
- scipy, scikit-learn - Statistical analysis

**All dependencies:** See `requirements.txt`

## 7) Environment variables

**Required:**
- `ANTHROPIC_API_KEY` - Claude API key for report generation

**Optional:**
- `PINECONE_API_KEY` - Pinecone vector database (optional)
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `CMS_API_BASE_URL` - CMS API base URL (has default)
- `CMS_DATASET_ID` - CMS dataset ID (has default: mj5m-pzi6)
- `WEB_SEARCH_ENABLED` - Enable web search (default: true)
- `WEB_SEARCH_PROVIDER` - Search provider (default: duckduckgo)
- `LOG_LEVEL` - Logging level (default: INFO)

**See:** `.env.template` for full list

## 8) Next steps

**Immediate:**
1. Test with multiple real NPIs (high-risk and low-risk)
2. Validate performance (<30 seconds consistently)
3. Monitor API costs (<$5/month target)

**Short-term:**
1. Enhance peer baseline calculation with real CMS data
2. Add batch processing for multiple providers
3. Improve temporal pattern analysis

**Long-term:**
1. User acceptance testing with fraud investigators
2. Performance optimization if needed
3. Advanced fraud pattern detection algorithms

## 9) Known issues

**Minor:**
- CMS API response format may vary (handled with fallbacks)
- Peer baseline uses default values (not real CMS peer data)
- Pinecone integration is optional and not fully utilized

**None Critical:** All core functionality works as expected.

## 10) Deployment

**Current:** Local development only
- Run: `streamlit run app.py`
- Access: `http://localhost:8501`

**Future:** Could deploy to:
- Streamlit Cloud (free tier available)
- Docker container
- Cloud VM (AWS, GCP, Azure)

**Not yet configured:** No production deployment setup yet.

---

**Status:** ✅ Phase 1 Complete | 🟡 Phase 2 In Planning
