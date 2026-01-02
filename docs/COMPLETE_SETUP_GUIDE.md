# 🚀 CardioGuard_AI - Complete Fresh Setup Guide

## 📋 What You Have vs What You Need

### ✅ What You Currently Have:
1. **BUMPY Source Code** (in project knowledge)
   - Complete multi-agent architecture
   - agents/, services/, orchestration/ folders
   - streamlit_app.py, langgraph_workflow.py, etc.
   
2. **CardioGuard_AI Documentation** (downloaded files)
   - Transformation specifications
   - Build plans and requirements
   - API integration guides

### 🎯 What We'll Create:
**Complete CardioGuard_AI system** by transforming BUMPY → healthcare fraud detection

## 📂 Step 1: Create Project Structure

### Create Base Directory
```bash
# Navigate to your workspace
cd /Users/chiho/ai-lab

# Create new CardioGuard_AI project
mkdir CardioGuard_AI
cd CardioGuard_AI

# Create docs folder for downloaded documentation
mkdir docs
```

### Download Documentation Files
```bash
# Move your downloaded files to docs/
# These 10 files should go in docs/:
# - README_CardioGuard_AI.md
# - PREWORK_SETUP.md  
# - BUILD_PLAN_1DAY.md
# - PRD_CardioGuard_AI_FI.md
# - TECH_REQUIREMENTS.md
# - AGENT_ARCHITECTURE.md
# - DATA_SOURCES.md
# - CURSOR_DEVELOPMENT.md
# - TESTING_VALIDATION.md
# - requirements.txt

# Verify documentation ready
ls docs/
# Should show all 10 files
```

## 📂 Step 2: Setup BUMPY Source Code

Since the BUMPY files are in project knowledge, I'll provide them for you to recreate locally:

### Create BUMPY Source Structure
```bash
# Create directory structure matching original BUMPY
mkdir -p {agents,services,orchestration,data_processors,utils}
mkdir -p data/{qdrant_db,reports}
mkdir -p logs
```

### Key BUMPY Files You Need

I'll create the essential BUMPY files so you have the complete source code to transform:

**BUMPT Architecture:**
- **agents/**: base_agent.py, supervisor_agent.py, research_agent.py, writer_agent.py, editor_agent.py, evaluator_agent.py
- **services/**: data_services.py, vector_service.py
- **orchestration/**: langgraph_workflow.py
- **Root files**: streamlit_app.py, config.py, models.py, requirements.txt

## 📂 Step 3: Environment Setup

### Python Environment
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install base dependencies (will update later)
pip install --upgrade pip setuptools wheel
```

### API Keys Configuration
```bash
# Copy environment template
cp docs/requirements.txt ./requirements.txt

# Create environment file
touch .env
echo "# CardioGuard_AI Environment Variables" > .env
echo "ANTHROPIC_API_KEY=your_claude_api_key_here" >> .env
echo "PINECONE_API_KEY=your_pinecone_api_key_here" >> .env
echo "PINECONE_ENVIRONMENT=your_pinecone_environment" >> .env
echo "MAX_MONTHLY_API_COST=5.00" >> .env
```

## 🎯 Step 4: BUMPY → CardioGuard_AI Transformation Plan

### File Mapping Strategy:
```
BUMPY → CardioGuard_AI Transformation:

agents/
├── base_agent.py → base_agent.py (minimal changes)
├── supervisor_agent.py → fraud_supervisor_agent.py (adapt workflow)
├── research_agent.py → fraud_research_agent.py (RITIS → CMS/OIG)
├── writer_agent.py → fraud_writer_agent.py (traffic → investigation reports)
├── editor_agent.py → fraud_editor_agent.py (adapt content focus)
└── evaluator_agent.py → fraud_evaluator_agent.py (adapt validation)

services/
├── data_services.py → healthcare_data_services.py (RITIS → CMS/OIG APIs)
└── vector_service.py → vector_service.py (Qdrant → Pinecone)

orchestration/
└── langgraph_workflow.py → fraud_workflow.py (preserve patterns, adapt context)

Root Files:
├── streamlit_app.py → streamlit_app.py (traffic UI → fraud investigation UI)
├── config.py → config.py (extend for healthcare APIs)
├── models.py → models.py (traffic models → healthcare fraud models)
└── requirements.txt → requirements.txt (update for free tools)
```

### Key Transformations:
1. **Data Sources**: RITIS traffic data → CMS + OIG healthcare data
2. **Analysis Focus**: Traffic patterns → Billing fraud patterns
3. **Output Format**: Traffic reports → Investigation reports
4. **Vector DB**: Qdrant (local) → Pinecone (your free account)
5. **LLM**: OpenAI GPT-4o → Claude Haiku (cost optimization)

## 🚀 Step 5: Cursor Development Strategy

### Open Project in Cursor
```bash
# From CardioGuard_AI directory
cursor .
```

### Cursor Pro Development Approach

**Phase 1: Foundation (1 hour)**
Use **Composer** for architectural analysis and planning:

```
I have the complete BUMPY multi-agent system and need to transform it into CardioGuard_AI for healthcare fraud detection.

CURRENT BUMPY SYSTEM:
- Multi-agent architecture: Supervisor → Research → Writer → Editor → Evaluator
- Data: RITIS traffic APIs
- Vector DB: Qdrant (local)
- LLM: OpenAI GPT-4o
- UI: Streamlit for traffic analysis

TARGET CARDIOGUARD_AI SYSTEM:
- Same agent architecture (preserve patterns)
- Data: CMS + OIG healthcare APIs (free)
- Vector DB: Pinecone (my existing free account)  
- LLM: Claude Haiku (cost optimization)
- UI: Streamlit for fraud investigation

TRANSFORMATION REQUIREMENTS:
1. Read docs/ folder for complete transformation specifications
2. Adapt existing agents for healthcare fraud detection (95% code reuse)
3. Change data sources from traffic → healthcare  
4. Update models from traffic incidents → provider fraud patterns
5. Preserve all multi-agent coordination patterns

Please analyze the BUMPT codebase and create a comprehensive transformation plan using Cursor Pro capabilities.
```

**Phase 2: Data Services (1 hour)**
Transform data_services.py from RITIS → CMS/OIG APIs using specific Cursor prompts from CURSOR_DEVELOPMENT.md

**Phase 3: Agent Adaptation (2 hours)**
Adapt each agent systematically using component guides

**Phase 4: UI & Integration (1 hour)**
Transform Streamlit UI for fraud investigation workflow

**Phase 5: Testing (1 hour)**
Validate using test cases from TESTING_VALIDATION.md

## ✅ Success Validation

### System Ready When:
1. **Input**: Provider NPI → **Output**: Fraud investigation report
2. **Processing Time**: <30 seconds per analysis
3. **Cost**: <$5/month total operating cost
4. **Accuracy**: >90% on known fraud test cases
5. **UI**: Professional interface for fraud investigators

## 📋 Next Steps Summary

### Immediate Actions:
1. ✅ Create `/Users/chiho/ai-lab/CardioGuard_AI` directory
2. ✅ Move downloaded docs to `docs/` folder  
3. ✅ Setup Python environment and basic structure
4. ✅ Configure API keys in .env file

### Cursor Development (4-6 hours):
1. 🚀 Open Cursor in CardioGuard_AI directory
2. 🤖 Use Composer for architectural transformation planning
3. 🔄 Transform TRAFFIX components systematically
4. 🧪 Test and validate fraud detection capabilities

### Final Deliverable:
**Working healthcare fraud detection system** that processes Provider NPIs and generates investigation reports with evidence and recommendations.

## 💡 Key Advantages

✅ **Proven Architecture**: TRAFFIX multi-agent system is battle-tested  
✅ **95% Code Reuse**: Minimal rewrites, maximum efficiency  
✅ **Free Tools Focus**: <$5/month operating cost  
✅ **Cursor Pro Power**: Advanced models for sophisticated transformation  
✅ **Complete Documentation**: Every aspect planned and specified  

**Ready to start with directory creation and environment setup?**

---

*This guide provides complete instructions for transforming TRAFFIX into CardioGuard_AI using your existing codebase and Cursor Pro capabilities.*
