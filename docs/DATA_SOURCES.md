# Data Sources Integration Guide - CardioGuard_AI

## 🎯 Purpose
Reference for healthcare data source integration to minimize token usage during API development.

## 📊 Data Sources Overview (100% Free)

### Primary Sources
1. **CMS Open Data** - Provider utilization patterns
2. **OIG Exclusion Database** - Sanctioned providers  
3. **NPPES Registry** - Provider credentials
4. **State Medical Boards** - License status (optional)

## 🏥 CMS Open Data Integration

### API Endpoint
```
Base URL: https://data.cms.gov/api/1/
Documentation: https://www.cms.gov/about-cms/information-systems/open-data
Cost: Free
Rate Limits: Reasonable usage (no strict limits)
```

### Key Datasets
```python
CMS_DATASETS = {
    "provider_utilization": {
        "endpoint": "/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service",
        "fields": ["npi", "nppes_provider_last_org_name", "nppes_provider_first_name", 
                  "provider_type", "medicare_participation_indicator", "line_srvc_cnt",
                  "bene_unique_cnt", "total_sbmtd_chrg", "total_medicare_payment_amt"],
        "use_case": "Billing pattern analysis and peer comparison"
    },
    "hospital_compare": {
        "endpoint": "/provider-data/dataset/xubh-q36u", 
        "fields": ["provider_id", "hospital_name", "hospital_overall_rating"],
        "use_case": "Hospital quality correlation with providers"
    }
}
```

### Implementation Pattern
```python
class CMSDataService:
    def __init__(self):
        self.base_url = "https://data.cms.gov/api/1/"
        self.session = requests.Session()
        
    async def get_provider_utilization(self, npi: str) -> dict:
        """Get provider utilization data from CMS."""
        try:
            url = f"{self.base_url}/provider-summary-by-type-of-service/..."
            params = {"npi": npi}
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                return self._process_cms_response(response.json())
            else:
                return {"error": f"CMS API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"CMS connection failed: {str(e)}"}
    
    def _process_cms_response(self, raw_data: dict) -> dict:
        """Process CMS API response into standardized format."""
        if not raw_data.get('data'):
            return {"error": "No CMS data found for provider"}
            
        # Extract key utilization metrics
        provider_data = raw_data['data'][0] if raw_data['data'] else {}
        
        return {
            "total_services": provider_data.get('line_srvc_cnt', 0),
            "unique_beneficiaries": provider_data.get('bene_unique_cnt', 0),
            "total_charges": provider_data.get('total_sbmtd_chrg', 0),
            "total_payments": provider_data.get('total_medicare_payment_amt', 0),
            "provider_type": provider_data.get('provider_type', 'Unknown'),
            "medicare_participation": provider_data.get('medicare_participation_indicator', 'Unknown')
        }
```

### Fraud Detection Metrics
- **Services per Beneficiary:** Unusual volume patterns
- **Charge to Payment Ratio:** Billing efficiency analysis
- **Provider Type Consistency:** Specialty vs service alignment
- **Medicare Participation:** Program compliance status

---

## 🚫 OIG Exclusion Database Integration

### Data Access
```
URL: https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv
Format: CSV file
Update Frequency: Monthly
Size: ~50MB
Authentication: None required
```

### File Structure
```python
OIG_COLUMNS = {
    "NPI": "Provider NPI identifier",
    "FIRSTNAME": "Provider first name", 
    "LASTNAME": "Provider last name",
    "EXCLTYPE": "Exclusion type code",
    "EXCLDATE": "Exclusion effective date",
    "REINSTDATE": "Reinstatement date (if applicable)",
    "WVRDATE": "Waiver date (if applicable)",
    "STATE": "Provider state"
}

EXCLUSION_TYPES = {
    "1128a1": "Mandatory - Medicare/Medicaid conviction",
    "1128a2": "Mandatory - Patient abuse conviction", 
    "1128a3": "Mandatory - Felony conviction",
    "1128b1": "Permissive - Misdemeanor conviction",
    "1128b2": "Permissive - License revocation",
    "1128b4": "Permissive - Default on health education loan"
}
```

### Implementation Pattern
```python
class OIGDataService:
    def __init__(self):
        self.exclusions_url = "https://oig.hhs.gov/exclusions/downloadables/UPDATED.csv"
        self.cache_file = "data/cache/oig_exclusions.csv"
        self.cache_duration = 30 * 24 * 3600  # 30 days in seconds
        
    async def check_provider_exclusion(self, npi: str) -> dict:
        """Check if provider is on OIG exclusion list."""
        try:
            exclusions_data = await self._get_exclusions_data()
            
            # Search for provider NPI in exclusions
            provider_exclusions = exclusions_data[exclusions_data['NPI'] == npi]
            
            if not provider_exclusions.empty:
                return self._format_exclusion_data(provider_exclusions.iloc[0])
            else:
                return {
                    "excluded": False,
                    "exclusion_status": "Not excluded",
                    "last_checked": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": f"OIG exclusion check failed: {str(e)}"}
    
    async def _get_exclusions_data(self) -> pd.DataFrame:
        """Get OIG exclusions data with caching."""
        # Check if cached data exists and is recent
        if self._is_cache_valid():
            return pd.read_csv(self.cache_file)
        
        # Download fresh data
        response = requests.get(self.exclusions_url)
        if response.status_code == 200:
            # Cache the data
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                f.write(response.content)
            
            return pd.read_csv(self.cache_file)
        else:
            raise Exception(f"Failed to download OIG data: {response.status_code}")
    
    def _format_exclusion_data(self, exclusion_record: pd.Series) -> dict:
        """Format exclusion data for analysis."""
        return {
            "excluded": True,
            "exclusion_type": exclusion_record.get('EXCLTYPE', 'Unknown'),
            "exclusion_date": exclusion_record.get('EXCLDATE', 'Unknown'),
            "reinstatement_date": exclusion_record.get('REINSTDATE', None),
            "exclusion_description": EXCLUSION_TYPES.get(exclusion_record.get('EXCLTYPE'), 'Unknown exclusion type'),
            "provider_name": f"{exclusion_record.get('FIRSTNAME', '')} {exclusion_record.get('LASTNAME', '')}".strip(),
            "state": exclusion_record.get('STATE', 'Unknown')
        }
```

### Fraud Risk Indicators
- **Current Exclusion:** Active sanctions
- **Exclusion History:** Past enforcement actions
- **Exclusion Type:** Severity of violations
- **Reinstatement Status:** Compliance rehabilitation

---

## 🆔 NPPES Registry Integration

### Data Access
```
Base URL: https://download.cms.gov/nppes/
API Endpoint: https://npiregistry.cms.hhs.gov/api/
Format: JSON API + CSV bulk downloads
Update Frequency: Weekly
Authentication: None required
```

### API Integration
```python
class NPPESDataService:
    def __init__(self):
        self.api_url = "https://npiregistry.cms.hhs.gov/api/"
        
    async def get_provider_details(self, npi: str) -> dict:
        """Get provider details from NPPES registry."""
        try:
            params = {
                "number": npi,
                "pretty": "true"
            }
            
            response = requests.get(self.api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result_count', 0) > 0:
                    return self._process_nppes_response(data['results'][0])
                else:
                    return {"error": "Provider not found in NPPES registry"}
            else:
                return {"error": f"NPPES API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"NPPES connection failed: {str(e)}"}
    
    def _process_nppes_response(self, provider_data: dict) -> dict:
        """Process NPPES API response."""
        basic_info = provider_data.get('basic', {})
        addresses = provider_data.get('addresses', [])
        practice_address = next((addr for addr in addresses if addr.get('address_purpose') == 'LOCATION'), {})
        
        return {
            "npi": provider_data.get('number'),
            "name": {
                "first": basic_info.get('first_name'),
                "last": basic_info.get('last_name'),
                "organization": basic_info.get('organization_name')
            },
            "credentials": basic_info.get('credential', ''),
            "gender": basic_info.get('gender'),
            "enumeration_date": basic_info.get('enumeration_date'),
            "certification_date": basic_info.get('certification_date'),
            "practice_location": {
                "address": practice_address.get('address_1', ''),
                "city": practice_address.get('city', ''),
                "state": practice_address.get('state', ''),
                "postal_code": practice_address.get('postal_code', '')
            },
            "taxonomies": [
                {
                    "code": tax.get('code'),
                    "description": tax.get('desc'),
                    "license": tax.get('license'),
                    "state": tax.get('state')
                }
                for tax in provider_data.get('taxonomies', [])
            ]
        }
```

### Provider Validation Uses
- **License Verification:** Active license status
- **Specialty Validation:** Service alignment with training
- **Practice Location:** Geographic service area analysis
- **Credential Verification:** Professional qualifications

---

## 📈 Peer Comparison Framework

### Peer Group Definition
```python
def identify_peer_providers(target_provider: dict) -> list:
    """Identify peer providers for baseline comparison."""
    peer_criteria = {
        "specialty": target_provider.get('specialty'),
        "practice_location": {
            "state": target_provider.get('practice_location', {}).get('state'),
            "urban_rural": classify_location(target_provider.get('practice_location'))
        },
        "provider_type": target_provider.get('provider_type'),
        "medicare_participation": target_provider.get('medicare_participation')
    }
    
    # Query CMS data for matching providers
    return query_peer_providers(peer_criteria, limit=50)

def calculate_peer_baselines(peer_providers: list) -> dict:
    """Calculate statistical baselines from peer group."""
    if len(peer_providers) < 10:
        return {"error": "Insufficient peer data for comparison"}
    
    metrics = ['total_services', 'unique_beneficiaries', 'total_charges', 'total_payments']
    baselines = {}
    
    for metric in metrics:
        values = [p.get(metric, 0) for p in peer_providers if p.get(metric)]
        if values:
            baselines[metric] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "median": np.median(values),
                "percentile_25": np.percentile(values, 25),
                "percentile_75": np.percentile(values, 75),
                "percentile_90": np.percentile(values, 90)
            }
    
    return baselines
```

## 🔧 Error Handling & Caching

### Resilient Data Collection
```python
class DataCollectionStrategy:
    async def collect_all_sources(self, npi: str) -> dict:
        """Collect data from all sources with error handling."""
        results = {}
        
        # Parallel data collection with error isolation
        tasks = [
            self.cms_service.get_provider_utilization(npi),
            self.oig_service.check_provider_exclusion(npi),
            self.nppes_service.get_provider_details(npi)
        ]
        
        cms_data, oig_data, nppes_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle individual source failures
        results['cms'] = cms_data if not isinstance(cms_data, Exception) else {"error": str(cms_data)}
        results['oig'] = oig_data if not isinstance(oig_data, Exception) else {"error": str(oig_data)}
        results['nppes'] = nppes_data if not isinstance(nppes_data, Exception) else {"error": str(nppes_data)}
        
        # Calculate data quality score
        results['data_quality'] = self._assess_data_quality(results)
        
        return results
```

### Caching Strategy
- **CMS Data:** 24-hour cache for provider utilization
- **OIG Data:** 30-day cache for exclusion list
- **NPPES Data:** 7-day cache for provider details
- **Analysis Results:** 1-hour cache for fraud analysis

---

*This guide provides complete data integration patterns for efficient development with minimal API debugging.*
