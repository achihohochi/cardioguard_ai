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
        "criminal conviction", "felony", "misdemeanor", "prison", "jail",
        "guilty plea", "pleaded guilty", "plea agreement", "criminal case",
        "theft", "fraud", "embezzlement", "healthcare fraud", "medicare fraud",
        "defrauded", "stole", "stolen", "theft", "criminal", "felony conviction"
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
        
        logger.info(f"Parsing {len(search_results)} web search results for NPI {npi} (provider: {provider_name})")
        
        for idx, result in enumerate(search_results):
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            url = result.get('url', '')
            
            # Keep original case for description, but use lowercase for analysis
            title_lower = title.lower()
            snippet_lower = snippet.lower()
            
            # Combine title and snippet for analysis
            text = f"{title_lower} {snippet_lower}"
            
            # Determine case type and status
            case_type, status = self._classify_legal_case(text)
            
            if case_type:
                # Extract date if available (use original case text)
                date = self._extract_date(f"{title} {snippet}")
                
                # Check if from official source (needed for threshold calculation)
                verified = self._is_official_source(url)
                
                # Calculate relevance score (pass case_type for conviction boosting)
                relevance_score = self._calculate_relevance(
                    text, url, provider_name, npi, specialty, location, case_type
                )
                
                # CRITICAL: Remove relevance threshold entirely for convictions
                # Convictions are too important to filter out - if classified as conviction, always include
                # Other case types still use 0.3 threshold
                relevance_threshold = 0.0 if case_type == "conviction" else 0.3
                
                # Log each result being processed
                logger.info(
                    f"Legal parser: NPI {npi}, case_type={case_type}, "
                    f"relevance_score={relevance_score:.2f}, threshold={relevance_threshold:.2f}, "
                    f"passes_threshold={relevance_score >= relevance_threshold}"
                )
                
                # Only include if relevance is above threshold (or if conviction, always include)
                if relevance_score >= relevance_threshold:
                    if case_type == "conviction" and relevance_score < 0.25:
                        logger.warning(
                            f"Conviction detected with low relevance ({relevance_score:.2f}) for NPI {npi}, "
                            f"but including anyway due to conviction classification"
                        )
                    # Build description (use original case for readability)
                    description = self._build_description(title, snippet, case_type, status)
                    
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
                    logger.debug(
                        f"Added legal info #{idx+1}: case_type={case_type}, "
                        f"relevance={relevance_score:.2f}, verified={verified}"
                    )
                else:
                    logger.debug(
                        f"Skipped result #{idx+1}: case_type={case_type}, "
                        f"relevance={relevance_score:.2f} < threshold={relevance_threshold:.2f}"
                    )
            else:
                logger.debug(f"Result #{idx+1} did not match any legal case type")
        
        # Sort by relevance score (highest first)
        legal_info_list.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Remove duplicates (same case_type + similar description)
        unique_legal_info = self._deduplicate(legal_info_list)
        
        # Count convictions for logging
        conviction_count = sum(1 for info in unique_legal_info if info.case_type == "conviction")
        
        logger.info(
            f"Parsed {len(unique_legal_info)} legal information items from {len(search_results)} search results "
            f"(convictions: {conviction_count})"
        )
        
        if conviction_count > 0:
            logger.warning(f"Found {conviction_count} conviction(s) for NPI {npi}")
        
        return unique_legal_info
    
    def _classify_legal_case(self, text: str) -> tuple[Optional[str], str]:
        """Classify legal case type and status from text."""
        text_lower = text.lower()
        
        # PRIORITY 1: Check for convictions FIRST (most serious)
        # CRITICAL FIX: If ANY conviction indicator is found, classify as conviction (don't require additional keywords)
        conviction_indicators = [
            "convicted", "sentenced", "pleaded guilty", "plea deal", "found guilty",
            "criminal conviction", "felony", "guilty plea", "plea agreement",
            "sentenced to", "prison", "jail", "criminal case", "plea bargain",
            "criminal", "felony conviction", "misdemeanor conviction",
            # Additional variations and edge cases
            "plead guilty", "pleads guilty", "pleading guilty",
            "conviction", "convictions", "criminal charges",
            "felony charges", "criminal offense", "criminal offenses",
            "serving time", "served time", "time served",
            "incarcerated", "incarceration", "imprisoned"
        ]
        if any(keyword in text_lower for keyword in conviction_indicators):
            # If ANY conviction indicator found, classify as conviction
            # This ensures felons are caught even if text doesn't have "strong" keywords
            logger.debug(f"Conviction classified based on keywords in text: {text_lower[:100]}")
            return "conviction", "convicted"
        
        # PRIORITY 2: Check for settlements (but not if conviction already found)
        if any(keyword in text_lower for keyword in self.SETTLEMENT_KEYWORDS):
            return "lawsuit", "settled"
        
        # PRIORITY 3: Check for pending/alleged
        if any(keyword in text_lower for keyword in self.PENDING_KEYWORDS):
            if "lawsuit" in text_lower or "sued" in text_lower:
                return "lawsuit", "pending"
            else:
                return "allegation", "pending"
        
        # PRIORITY 4: Check for lawsuits
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
        location: Optional[str],
        case_type: Optional[str] = None
    ) -> float:
        """Calculate relevance score (0.0-1.0) for search result."""
        score = 0.0
        text_lower = text.lower()
        url_lower = url.lower()
        name_lower = provider_name.lower()
        
        # CRITICAL: Boost relevance for conviction-related keywords even without name match
        # This ensures convictions aren't filtered out due to low relevance
        conviction_keywords_in_text = [
            "convicted", "felony", "sentenced", "pleaded guilty", "found guilty",
            "criminal conviction", "prison", "jail", "plea deal", "plea agreement"
        ]
        if any(keyword in text_lower for keyword in conviction_keywords_in_text):
            score += 0.3  # Conviction keyword bonus
        
        # Check URL for conviction indicators (court case numbers, criminal, etc.)
        if any(keyword in url_lower for keyword in ["criminal", "court", "case", "conviction"]):
            score += 0.2  # URL-based conviction indicator
        
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
        
        # CRITICAL: If this is a classified conviction, ensure minimum relevance score
        # This prevents valid convictions from being filtered out
        if case_type == "conviction" and score < 0.25:
            score = 0.25  # Minimum relevance for convictions (above 0.2 threshold)
        
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
    
    def _extract_fraud_amounts(self, text: str, case_type: str, status: str) -> Dict[str, Optional[float]]:
        """Extract fraud dollar amounts from legal text.
        
        Returns dictionary with:
        - estimated_fraud_amount: Amount stolen/defrauded
        - settlement_amount: Settlement amount if settled
        - restitution_amount: Court-ordered restitution
        """
        amounts = {
            'estimated_fraud_amount': None,
            'settlement_amount': None,
            'restitution_amount': None
        }
        
        text_lower = text.lower()
        
        # Pattern to match dollar amounts: $X, $X million, $X billion, $XM, $XB, etc.
        # Match patterns like: $5 million, $2.3M, $1.2 billion, $500,000, $2M, etc.
        dollar_patterns = [
            # Pattern 1: $X million/billion (with word)
            r'\$[\d,]+\.?\d*\s*(million|billion|m|b|M|B)\b',
            # Pattern 2: $XM or $XB (compact format)
            r'\$[\d,]+\.?\d*[mMbB]\b',
            # Pattern 3: $X,XXX,XXX (full number format)
            r'\$[\d,]{4,}\b',
            # Pattern 4: $XXX,XXX (thousands format)
            r'\$[\d]{1,3}(?:,\d{3})+\b',
            # Pattern 5: $X (simple format, might be thousands or millions)
            r'\$[\d,]+\.?\d*\b'
        ]
        
        all_amounts = []
        for pattern in dollar_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(0)
                amount_value = self._parse_dollar_amount(amount_str)
                if amount_value and amount_value > 0:
                    all_amounts.append((amount_value, match.start(), match.end()))
        
        # Sort by position in text (first mentioned is usually most relevant)
        all_amounts.sort(key=lambda x: x[1])
        
        # Determine amount type based on context around the amount
        for amount_value, start_pos, end_pos in all_amounts:
            # Get context around the amount (50 chars before and after)
            context_start = max(0, start_pos - 50)
            context_end = min(len(text), end_pos + 50)
            context = text[context_start:context_end].lower()
            
            # Check for settlement keywords
            if any(keyword in context for keyword in ['settled', 'settlement', 'agreed to pay', 'paid']):
                if amounts['settlement_amount'] is None or amount_value > amounts['settlement_amount']:
                    amounts['settlement_amount'] = amount_value
            
            # Check for restitution keywords
            elif any(keyword in context for keyword in ['restitution', 'ordered to pay', 'must pay', 'reimburse']):
                if amounts['restitution_amount'] is None or amount_value > amounts['restitution_amount']:
                    amounts['restitution_amount'] = amount_value
            
            # Check for fraud/theft keywords (estimated fraud)
            elif any(keyword in context for keyword in ['fraud', 'stole', 'stolen', 'defrauded', 'embezzled', 'theft']):
                if amounts['estimated_fraud_amount'] is None or amount_value > amounts['estimated_fraud_amount']:
                    amounts['estimated_fraud_amount'] = amount_value
            
            # Default: if it's a conviction case, assume it's fraud amount
            elif case_type == 'conviction':
                if amounts['estimated_fraud_amount'] is None or amount_value > amounts['estimated_fraud_amount']:
                    amounts['estimated_fraud_amount'] = amount_value
            
            # If settled case, default to settlement amount
            elif status == 'settled' and amounts['settlement_amount'] is None:
                amounts['settlement_amount'] = amount_value
        
        return amounts
    
    def _parse_dollar_amount(self, amount_str: str) -> Optional[float]:
        """Parse dollar amount string to float value.
        
        Examples:
        - "$5 million" -> 5,000,000
        - "$2.3M" -> 2,300,000
        - "$1.2 billion" -> 1,200,000,000
        - "$500,000" -> 500,000
        - "$2M" -> 2,000,000
        """
        try:
            # Remove $ and commas
            clean_str = amount_str.replace('$', '').replace(',', '').strip()
            
            # Check for million/billion indicators
            if 'billion' in clean_str.lower() or clean_str.lower().endswith('b'):
                # Remove 'billion' or 'b'
                num_str = re.sub(r'[bB]illion|[bB]\b', '', clean_str).strip()
                if num_str:
                    return float(num_str) * 1_000_000_000
            
            elif 'million' in clean_str.lower() or clean_str.lower().endswith('m'):
                # Remove 'million' or 'm'
                num_str = re.sub(r'[mM]illion|[mM]\b', '', clean_str).strip()
                if num_str:
                    return float(num_str) * 1_000_000
            
            elif 'thousand' in clean_str.lower() or clean_str.lower().endswith('k'):
                # Remove 'thousand' or 'k'
                num_str = re.sub(r'[tT]housand|[kK]\b', '', clean_str).strip()
                if num_str:
                    return float(num_str) * 1_000
            
            else:
                # Just a number
                return float(clean_str)
        
        except (ValueError, AttributeError):
            return None
        
        return None
    
    def extract_fraud_financial_data(self, legal_info: LegalInformation) -> Optional[Dict[str, Any]]:
        """Extract fraud financial data from a LegalInformation object.
        
        Returns dictionary compatible with FraudFinancialData model, or None if no amounts found.
        """
        # Get original text from description (remove the case_type prefix we added)
        description = legal_info.description
        if ':' in description:
            description = description.split(':', 1)[1].strip()
        
        # Extract amounts
        amounts = self._extract_fraud_amounts(description, legal_info.case_type, legal_info.status)
        
        # If no amounts found, return None
        if not any(amounts.values()):
            return None
        
        # Extract year from date if available
        investigation_year = None
        if legal_info.date:
            year_match = re.search(r'\b(19|20)\d{2}\b', legal_info.date)
            if year_match:
                try:
                    investigation_year = int(year_match.group(0))
                except:
                    pass
        
        # Determine source
        source = "Court records" if legal_info.verified else "Public records"
        if legal_info.case_type == "conviction":
            source = "Court conviction records"
        elif legal_info.status == "settled":
            source = "Settlement records"
        
        # Build notes
        notes_parts = []
        if amounts['estimated_fraud_amount']:
            notes_parts.append(f"Estimated fraud: ${amounts['estimated_fraud_amount']:,.0f}")
        if amounts['settlement_amount']:
            notes_parts.append(f"Settlement: ${amounts['settlement_amount']:,.0f}")
        if amounts['restitution_amount']:
            notes_parts.append(f"Restitution: ${amounts['restitution_amount']:,.0f}")
        notes = "; ".join(notes_parts) if notes_parts else None
        
        return {
            'estimated_fraud_amount': amounts['estimated_fraud_amount'],
            'settlement_amount': amounts['settlement_amount'],
            'restitution_amount': amounts['restitution_amount'],
            'investigation_year': investigation_year,
            'source': source,
            'notes': notes
        }
