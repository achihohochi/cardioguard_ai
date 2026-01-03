"""
CardioGuard_AI Services Package
Data collection and processing services.
"""

from .cms_service import CMSDataService
from .oig_service import OIGDataService
from .nppes_service import NPPESDataService
from .data_service import DataService
from .export_service import ExportService
from .web_search_service import WebSearchService
from .legal_parser_service import LegalParserService
from .fraud_financial_service import FraudFinancialService

# Pinecone is optional - import may fail if old package is installed
try:
    from .vector_service import VectorService
except Exception:
    VectorService = None  # Vector service will be unavailable

__all__ = [
    "CMSDataService",
    "OIGDataService",
    "NPPESDataService",
    "DataService",
    "ExportService",
    "WebSearchService",
    "LegalParserService",
    "FraudFinancialService",
]

# Add VectorService only if available
if VectorService is not None:
    __all__.append("VectorService")
