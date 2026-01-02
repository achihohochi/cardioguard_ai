"""
Web Search Service Tests
"""

import pytest
import asyncio
from services.web_search_service import WebSearchService
from services.legal_parser_service import LegalParserService


@pytest.mark.asyncio
async def test_web_search_service_basic():
    """Test basic web search functionality."""
    service = WebSearchService()
    
    # Test with known provider
    result = await service.search_provider_legal_info(
        provider_name="Scott Reuben",
        npi="1992796015",
        specialty="Anesthesiology"
    )
    
    assert "legal_results" in result
    assert "searches_performed" in result
    assert isinstance(result["legal_results"], list)
    
    await service.close()


@pytest.mark.asyncio
async def test_web_search_without_name():
    """Test web search gracefully handles missing name."""
    service = WebSearchService()
    
    result = await service.search_provider_legal_info(
        provider_name="",
        npi="1992796015",
        specialty=None
    )
    
    # Should return empty results, not error
    assert "legal_results" in result
    assert isinstance(result["legal_results"], list)
    
    await service.close()


def test_legal_parser_basic():
    """Test legal parser with sample search results."""
    parser = LegalParserService()
    
    # Sample search results
    search_results = [
        {
            "title": "Dr. John Smith Convicted of Healthcare Fraud",
            "snippet": "Dr. John Smith was convicted of healthcare fraud in 2023",
            "url": "https://court.gov/case123"
        },
        {
            "title": "Provider Lawsuit Settlement",
            "snippet": "NPI 1234567890 reached settlement in malpractice case",
            "url": "https://example.com"
        }
    ]
    
    legal_info = parser.parse_legal_information(
        search_results,
        provider_name="John Smith",
        npi="1234567890",
        specialty="Cardiology"
    )
    
    assert len(legal_info) > 0
    assert all(hasattr(li, 'case_type') for li in legal_info)
    assert all(hasattr(li, 'relevance_score') for li in legal_info)


def test_legal_parser_relevance_scoring():
    """Test relevance scoring for legal information."""
    parser = LegalParserService()
    
    # Result with NPI match (should have high relevance)
    search_results = [
        {
            "title": "Provider NPI 1992796015 Convicted",
            "snippet": "NPI 1992796015 was convicted of fraud",
            "url": "https://court.gov/case"
        }
    ]
    
    legal_info = parser.parse_legal_information(
        search_results,
        provider_name="Scott Reuben",
        npi="1992796015",
        specialty="Anesthesiology"
    )
    
    if legal_info:
        # NPI match should give high relevance
        assert legal_info[0].relevance_score >= 0.5


def test_legal_parser_case_classification():
    """Test legal case type classification."""
    parser = LegalParserService()
    
    # Test conviction detection
    conviction_text = "Dr. Smith was convicted of healthcare fraud"
    case_type, status = parser._classify_legal_case(conviction_text)
    assert case_type == "conviction"
    assert status == "convicted"
    
    # Test lawsuit detection
    lawsuit_text = "Provider sued for malpractice, case pending"
    case_type, status = parser._classify_legal_case(lawsuit_text)
    assert case_type == "lawsuit"
    assert status == "pending"
    
    # Test settlement detection
    settlement_text = "Provider reached settlement in fraud case"
    case_type, status = parser._classify_legal_case(settlement_text)
    assert case_type == "lawsuit"
    assert status == "settled"


if __name__ == "__main__":
    pytest.main([__file__])
