"""
End-to-End Workflow Tests
"""

import pytest
import asyncio
from workflow import analyze_provider_fraud_risk


@pytest.mark.asyncio
async def test_workflow_basic():
    """Test basic workflow execution."""
    # Note: This test requires valid API keys and may incur costs
    # Use a test NPI or mock data for actual testing
    
    # This is a placeholder test structure
    # Actual implementation would use test NPIs or mocked services
    pass


def test_npi_validation():
    """Test NPI format validation."""
    from models import ProviderProfile, ProviderName
    
    # Valid NPI
    try:
        profile = ProviderProfile(
            npi="1234567890",
            name=ProviderName()
        )
        assert profile.npi == "1234567890"
    except ValueError:
        pytest.fail("Valid NPI should not raise ValueError")
    
    # Invalid NPI (too short)
    with pytest.raises(ValueError):
        ProviderProfile(npi="12345", name=ProviderName())
    
    # Invalid NPI (non-numeric)
    with pytest.raises(ValueError):
        ProviderProfile(npi="123456789a", name=ProviderName())


if __name__ == "__main__":
    pytest.main([__file__])
