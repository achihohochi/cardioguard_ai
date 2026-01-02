"""
Legal Parser Service
Parse web search results to extract legal/court information.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LegalInformation


class LegalParserService:
    """Service for parsing legal information from web search results."""
    
    # Legal keywords for different case types
    CONVICTION_KEYWORDS = [
        "convicted", "sentenced", "pleaded guilty", "plea deal", "found guilty",
        "criminal conviction", "felony", "misdemeanor", "prison", "jail"
    ]
    
    LAWSUIT_KEYWORDS = [
        "lawsuit", "sued", "settlement", "litigation", "civil suit",
        "malpractice", "negligence", "damages", "plaintiff", "defendant"
    ]
    
    PENDING_KEYWORDS = [
        "pending", "alleged", "accused", "charges", "indictment",
        "under investigation", "facing charges", "charged with"
    ]
    
    SETTLEMENT_KEYWORDS = [
        "settled", "settlement", "agreed to pay", "reached settlement",
        "settled out of court"
    ]
    
    # Official source domains
    OFFICIAL_DOMAINS = [
        "court", "gov", "uscourts", "justice", "doj", "fbi",
        "state", "county", "district", "supreme"
    ]
    
    def parse_legal_information(
        self,
        search_results: List[Dict[str, Any]],
        provider_name: str,
        npi: str,
        specialty: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[LegalInformation]:
        """Parse search results to extract legal information."""
        legal_info_list = []
        
        for result in search_results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            url = result.get('url', '')
            
            # Combine title and snippet for analysis
            text = f"{title} {snippet}"
            
            # Determine case type and status
            case_type, status = self._classify_legal_case(text)
            
            if case_type:
                # Extract date if available
                date = self._extract_date(text)
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(
                    text, url, provider_name, npi, specialty, location
                )
                
                # Only include if relevance is above threshold
                if relevance_score >= 0.3:
                    # Build description
                    description = self._build_description(title, snippet, case_type, status)
                    
                    # Check if from official source
                    verified = self._is_official_source(url)
                    
                    legal_info = LegalInformation(
                        case_type=case_type,
                        status=status,
                        date=date,
                        description=description,
                        source_url=url,
                        relevance_score=relevance_score,
                        verified=verified
                    )
                    
                    legal_info_list.append(legal_info)
        
        # Sort by relevance score (highest first)
        legal_info_list.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Remove duplicates (same case_type + similar description)
        unique_legal_info = self._deduplicate(legal_info_list)
        
        logger.info(f"Parsed {len(unique_legal_info)} legal information items from {len(search_results)} search results")
        
        return unique_legal_info
    
    def _classify_legal_case(self, text: str) -> tuple[Optional[str], str]:
        """Classify legal case type and status from text."""
        text_lower = text.lower()
        
        # Check for convictions
        if any(keyword in text_lower for keyword in self.CONVICTION_KEYWORDS):
            return "conviction", "convicted"
        
        # Check for settlements
        if any(keyword in text_lower for keyword in self.SETTLEMENT_KEYWORDS):
            return "lawsuit", "settled"
        
        # Check for pending/alleged
        if any(keyword in text_lower for keyword in self.PENDING_KEYWORDS):
            if "lawsuit" in text_lower or "sued" in text_lower:
                return "lawsuit", "pending"
            else:
                return "allegation", "pending"
        
        # Check for lawsuits
        if any(keyword in text_lower for keyword in self.LAWSUIT_KEYWORDS):
            if "settled" in text_lower or "settlement" in text_lower:
                return "lawsuit", "settled"
            elif "dismissed" in text_lower:
                return "lawsuit", "dismissed"
            else:
                return "lawsuit", "pending"
        
        return None, "unknown"
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text if available."""
        # Look for common date patterns
        date_patterns = [
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}\b'  # Year only
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _calculate_relevance(
        self,
        text: str,
        url: str,
        provider_name: str,
        npi: str,
        specialty: Optional[str],
        location: Optional[str]
    ) -> float:
        """Calculate relevance score (0.0-1.0) for search result."""
        score = 0.0
        text_lower = text.lower()
        url_lower = url.lower()
        name_lower = provider_name.lower()
        
        # Match provider name in result: +0.3
        if name_lower in text_lower:
            score += 0.3
        
        # Match NPI in result: +0.5 (very strong indicator)
        if npi in text or npi in url:
            score += 0.5
        
        # Match specialty: +0.2
        if specialty and specialty.lower() in text_lower:
            score += 0.2
        
        # Match location: +0.2
        if location and location.lower() in text_lower:
            score += 0.2
        
        # Official court/government source: +0.5
        if self._is_official_source(url):
            score += 0.5
        
        # Recent date (<2 years): +0.3
        date = self._extract_date(text)
        if date:
            try:
                # Try to parse year
                year_match = re.search(r'\b(19|20)\d{2}\b', date)
                if year_match:
                    year = int(year_match.group(0))
                    current_year = datetime.now().year
                    if current_year - year <= 2:
                        score += 0.3
            except:
                pass
        
        # Cap at 1.0
        return min(1.0, score)
    
    def _is_official_source(self, url: str) -> bool:
        """Check if URL is from official source."""
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.OFFICIAL_DOMAINS)
    
    def _build_description(self, title: str, snippet: str, case_type: str, status: str) -> str:
        """Build description from title and snippet."""
        # Use title if available, otherwise use snippet
        description = title if title else snippet
        
        # Add case type and status context
        if case_type and status:
            description = f"{case_type.title()} ({status}): {description}"
        
        # Limit length
        if len(description) > 500:
            description = description[:497] + "..."
        
        return description
    
    def _deduplicate(self, legal_info_list: List[LegalInformation]) -> List[LegalInformation]:
        """Remove duplicate legal information items."""
        seen = set()
        unique = []
        
        for info in legal_info_list:
            # Create signature from case_type + first 50 chars of description
            signature = f"{info.case_type}_{info.status}_{info.description[:50]}"
            
            if signature not in seen:
                seen.add(signature)
                unique.append(info)
        
        return unique
