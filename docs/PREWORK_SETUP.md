# CardioGuard_AI - Pre-Work Setup (Save Cursor Tokens)

## 🎯 Objective
Complete all setup tasks BEFORE opening Cursor to maximize token efficiency for actual coding.

## ⏱️ Time Investment
**Total Pre-Work Time:** ~45 minutes  
**Cursor Token Savings:** 80-90% of setup tokens  
**Coding Focus:** Pure development in Cursor  

## 📋 Pre-Work Checklist

### Step 1: Environment Setup (15 minutes)

#### 1.1 Create Project Directory
```bash
# Navigate to your workspace
cd /Users/chiho/ai-lab

# Create CardioGuard_AI project
mkdir CardioGuard_AI
cd CardioGuard_AI

# Create basic directory structure
mkdir -p {agents,services,config,workflows,ui,data,tests,docs}
mkdir -p data/{sample,processed,cache}
mkdir -p docs/{components,api}

# Verify structure
tree -L 2
```

#### 1.2 Python Environment Setup
```bash
# Create virtual environment
python3.11 -m venv venv

# Activate environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Verify Python version
python --version  # Should be 3.11+
```

### Step 2: API Account Setup (10 minutes)

#### 2.1 Anthropic Claude API
```bash
# Visit: https://console.anthropic.com/
# Create account if needed
# Generate API key
# Copy key for later use
```

#### 2.2 Pinecone Vector Database
```bash
# Visit: https://www.pinecone.io/
# Sign up for free account (if not already have one)
# Create new index:
#   - Name: cardioguard-vectors
#   - Dimensions: 1536 (for OpenAI embeddings)
#   - Metric: cosine
#   - Pod Type: Starter (free)
# Copy API key and environment
```

#### 2.3 Free Data Source Access Verification
```bash
# Test CMS API access
curl "https://data.cms.gov/api/1/metastore/schemas/dataset/items" | head

# Test OIG exclusion list access  
curl -I "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"

# Both should return 200 OK status
```

### Step 3: Configuration Files (10 minutes)

#### 3.1 Create .env.template
```bash
# Create template file
cat > .env.template << 'EOF'
# API Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here

# Cost Controls
MAX_MONTHLY_API_COST=5.00
PREFERRED_MODEL=claude-3-haiku-20240307

# Data Sources (Pre-configured)
CMS_API_BASE_URL=https://data.cms.gov/api/1/
OIG_EXCLUSIONS_URL=https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv
NPPES_REGISTRY_URL=https://download.cms.gov/nppes/

# Application Settings
LOG_LEVEL=INFO
STREAMLIT_PORT=8501
CACHE_DURATION_HOURS=24
EOF
```

#### 3.2 Create .env with your actual keys
```bash
# Copy template
cp .env.template .env

# Edit .env with your actual API keys
# ANTHROPIC_API_KEY=your_actual_claude_key
# PINECONE_API_KEY=your_actual_pinecone_key  
# PINECONE_ENVIRONMENT=your_actual_environment

# Note: You'll need to manually edit .env with real keys
```

#### 3.3 Create .gitignore
```bash
cat > .gitignore << 'EOF'
# Environment
.env
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Data
data/cache/
data/processed/
*.csv
*.json
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/
EOF
```

### Step 4: Dependencies Installation (5 minutes)

#### 4.1 Create requirements.txt (Minimal Free Tools)
```bash
cat > requirements.txt << 'EOF'
# Core Framework
streamlit==1.31.0
pandas==2.1.4
numpy==1.24.4

# AI/ML
langchain==0.1.20
langchain-anthropic==0.1.15
anthropic==0.18.1

# Vector Database
pinecone-client==3.0.0

# Data Processing  
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.3

# Statistics
scipy==1.11.4
scikit-learn==1.3.2

# Utilities
python-dateutil==2.8.2
loguru==0.7.2

# Testing (minimal)
pytest==7.4.4
EOF
```

#### 4.2 Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Verify key packages
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import anthropic; print('Anthropic:', anthropic.__version__)"
python -c "import pinecone; print('Pinecone: OK')"
```

### Step 5: Sample Data Preparation (5 minutes)

#### 5.1 Download Test Data
```bash
# Create sample data directory
mkdir -p data/sample

# Download small sample of CMS data for testing
curl -o data/sample/cms_sample.csv "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service/data.csv?size=100"

# Create test provider data
cat > data/sample/test_providers.json << 'EOF'
{
  "known_fraud_case": {
    "npi": "1234567890",
    "name": "Dr. Test Fraud",
    "specialty": "Cardiology", 
    "expected_risk_score": 95,
    "fraud_indicators": ["billing_anomaly", "temporal_clustering"]
  },
  "normal_provider": {
    "npi": "0987654321",
    "name": "Dr. Normal Practice",
    "specialty": "Cardiology",
    "expected_risk_score": 15,
    "fraud_indicators": []
  }
}
EOF
```

## ✅ Pre-Work Validation

### Verify Setup Complete
```bash
# Check directory structure
ls -la

# Check environment
source venv/bin/activate
python --version
pip list | grep -E "(streamlit|anthropic|pinecone)"

# Check config files
cat .env.template
ls -la .env

# Check sample data
ls -la data/sample/

# Test API connectivity (optional)
python -c "
import anthropic
import pinecone
print('✅ All packages imported successfully')
"
```

### Setup Verification Checklist
- [ ] Project directory created with proper structure
- [ ] Python 3.11+ virtual environment activated
- [ ] All dependencies installed successfully
- [ ] .env file created with API keys
- [ ] Sample test data downloaded
- [ ] Git repository initialized (optional)

## 🚀 Ready for Cursor Development

### What You've Completed
✅ **Environment Setup:** Python venv + dependencies installed  
✅ **API Access:** Claude + Pinecone configured  
✅ **Data Sources:** CMS sample data ready  
✅ **Configuration:** All settings pre-configured  
✅ **Testing Data:** Validation cases prepared  

### Cursor Development Focus
🎯 **Pure Coding:** Agent architecture + fraud algorithms  
🎯 **Data Integration:** CMS/OIG processing  
🎯 **UI Development:** Streamlit interface  
🎯 **Testing:** End-to-end validation  

### Estimated Token Savings
- **Setup Tasks:** ~2,000 tokens saved
- **Environment Config:** ~1,500 tokens saved  
- **Data Preparation:** ~1,000 tokens saved
- **Documentation:** ~500 tokens saved
- **Total Saved:** ~5,000 tokens for actual development

## 📂 Next Steps

1. **Complete Pre-Work** (this checklist)
2. **Open Cursor** in CardioGuard_AI directory
3. **Load Documentation** (provided in package)
4. **Start Development** with focus on coding only

**Pre-work complete = Maximum Cursor efficiency for actual application development!**

---

*Complete this setup to maximize Cursor token efficiency and focus development time on core functionality.*
