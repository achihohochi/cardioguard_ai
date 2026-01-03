"""
Fraud Financial Data Storage Service
Simple JSON-based storage for fraud dollar amounts (MVP).
"""

import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import FraudFinancialData
from config import CACHE_DIR


class FraudFinancialService:
    """Service for storing and retrieving fraud financial data."""
    
    def __init__(self):
        self.storage_dir = CACHE_DIR.parent / "fraud_financial"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = self.storage_dir / "fraud_financial_data.json"
        self._data: Optional[Dict[str, List[Dict]]] = None
    
    def _load_data(self) -> Dict[str, List[Dict]]:
        """Load financial data from JSON file."""
        if self._data is not None:
            return self._data
        
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    self._data = json.load(f)
                    return self._data
            except Exception as e:
                logger.error(f"Failed to load fraud financial data: {e}")
                self._data = {}
                return self._data
        else:
            self._data = {}
            return self._data
    
    def _save_data(self):
        """Save financial data to JSON file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self._data, f, indent=2, default=str)
            logger.info(f"Saved fraud financial data to {self.storage_file}")
        except Exception as e:
            logger.error(f"Failed to save fraud financial data: {e}")
    
    def save_financial_data(self, npi: str, financial_data: FraudFinancialData):
        """Save financial data for a provider NPI."""
        data = self._load_data()
        
        # Convert to dict for storage
        financial_dict = financial_data.dict()
        
        # Initialize NPI entry if not exists
        if npi not in data:
            data[npi] = []
        
        # Add new entry
        data[npi].append(financial_dict)
        
        # Save
        self._data = data
        self._save_data()
        logger.info(f"Saved financial data for NPI {npi}: ${financial_data.total_fraud_impact:,.2f}")
    
    def get_financial_data(self, npi: str) -> Optional[FraudFinancialData]:
        """Get most recent financial data for a provider NPI."""
        data = self._load_data()
        
        if npi not in data or not data[npi]:
            return None
        
        # Get most recent entry
        most_recent = data[npi][-1]
        
        # Convert back to model
        try:
            return FraudFinancialData(**most_recent)
        except Exception as e:
            logger.error(f"Failed to parse financial data for NPI {npi}: {e}")
            return None
    
    def get_all_financial_data(self, npi: str) -> List[FraudFinancialData]:
        """Get all financial data entries for a provider NPI."""
        data = self._load_data()
        
        if npi not in data:
            return []
        
        result = []
        for entry in data[npi]:
            try:
                result.append(FraudFinancialData(**entry))
            except Exception as e:
                logger.error(f"Failed to parse financial data entry: {e}")
        
        return result
    
    def get_annual_total(self, year: int) -> float:
        """Get total fraud impact for a specific year."""
        data = self._load_data()
        total = 0.0
        
        for npi, entries in data.items():
            for entry in entries:
                entry_year = entry.get('investigation_year')
                if entry_year == year:
                    # Calculate total from entry
                    entry_total = 0.0
                    if entry.get('estimated_fraud_amount'):
                        entry_total += entry['estimated_fraud_amount']
                    if entry.get('settlement_amount'):
                        entry_total += entry['settlement_amount']
                    if entry.get('restitution_amount'):
                        entry_total += entry['restitution_amount']
                    total += entry_total
        
        return total
    
    def get_all_providers_with_financial_data(self) -> List[str]:
        """Get list of all NPIs that have financial data."""
        data = self._load_data()
        return list(data.keys())
