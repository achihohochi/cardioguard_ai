"""
Base Agent Class
Common functionality for all agents.
"""

from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CACHE_DIR


class BaseAgent:
    """Base class for all agents with common functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger
        self.cache_dir = CACHE_DIR / "agents"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.agent_name = self.__class__.__name__
    
    def log_activity(self, action: str, data: Optional[Dict] = None):
        """Log agent activity."""
        log_data = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        if data:
            log_data.update(data)
        
        self.logger.info(f"[{self.agent_name}] {action}", **log_data)
    
    def handle_error(self, error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """Standardized error handling."""
        error_msg = str(error)
        self.logger.error(f"[{self.agent_name}] Error: {error_msg}", exc_info=error)
        
        return {
            "error": True,
            "error_message": error_msg,
            "agent": self.agent_name,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Template method for agent execution."""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> tuple[bool, Optional[str]]:
        """Validate input data has required fields."""
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
