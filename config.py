"""
CardioGuard_AI Configuration Management
Handles environment variables, API settings, and application configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "cardioguard-vectors")

# Cost Controls
MAX_MONTHLY_API_COST = float(os.getenv("MAX_MONTHLY_API_COST", "5.00"))
PREFERRED_MODEL = os.getenv("PREFERRED_MODEL", "claude-3-haiku-20240307")
MAX_TOKENS_PER_REQUEST = int(os.getenv("MAX_TOKENS_PER_REQUEST", "1000"))

# Data Sources Configuration
CMS_API_BASE_URL = os.getenv("CMS_API_BASE_URL", "https://data.cms.gov/api/1/")
OIG_EXCLUSIONS_URL = os.getenv(
    "OIG_EXCLUSIONS_URL",
    "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
)
NPPES_API_URL = os.getenv(
    "NPPES_API_URL",
    "https://npiregistry.cms.hhs.gov/api/"
)

# Application Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Cache Configuration
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# CMS Cache: 24 hours
CMS_CACHE_DURATION = 24 * 3600  # seconds

# OIG Cache: 30 days
OIG_CACHE_DURATION = 30 * 24 * 3600  # seconds

# NPPES Cache: 7 days
NPPES_CACHE_DURATION = 7 * 24 * 3600  # seconds

# Analysis Cache: 1 hour
ANALYSIS_CACHE_DURATION = 3600  # seconds

# Pinecone Configuration
PINECONE_CONFIG = {
    "index_name": PINECONE_INDEX_NAME,
    "dimension": 1536,  # OpenAI embedding size
    "metric": "cosine",
    "pod_type": "starter",  # Free tier
    "max_vectors": 1000000,  # Free limit
}

# Risk Score Thresholds
RISK_THRESHOLDS = {
    "low": 30,
    "medium": 70,
    "high": 100
}

# Validation
def validate_config() -> tuple[bool, list[str]]:
    """Validate configuration and return (is_valid, errors)."""
    errors = []
    
    # Required: Anthropic API key for report generation
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY is not set (required for report generation)")
    
    # Optional: Pinecone (vector database is optional for MVP)
    # Only warn if partially configured
    if (PINECONE_API_KEY and not PINECONE_ENVIRONMENT) or (PINECONE_ENVIRONMENT and not PINECONE_API_KEY):
        errors.append("PINECONE_API_KEY and PINECONE_ENVIRONMENT must both be set if using Pinecone (optional)")
    
    return len(errors) == 0, errors
