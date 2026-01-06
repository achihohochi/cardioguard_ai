# Fraud Financial Data Source Analysis: NPI 1386756476

## Summary

The **$110,000,000 fraud amount** for NPI 1386756476 (CARLOS MUNOZ) was extracted from **Web Search** results, specifically from a news article discovered during the legal information discovery process.

---

## Data Source: Web Search (1 of 4 Sources)

### Source Details

**Primary Source:** Web Search Service  
**Search Query:** `"CARLOS MUNOZ" convicted healthcare fraud`  
**Search Provider:** DuckDuckGo  
**Results Retrieved:** 16 search results  
**Result Containing $110M:** Result #1 (first result)

### Exact Source Article

**Title:** "Houston health care fraud takedown targets $110 million scheme"  
**URL:** https://www.mytexasdaily.com/upper-gulf-coast/houston-health-care-fraud-takedown-targets-110-million-scheme/  
**Snippet Excerpt:**
> "In a related case, Carlos Munoz, 57, of Richmond, is charged with receiving kickbacks to certify patients for hospice services. Additionally, Keilan Peterson, 38, and Kimberly Martinez, 47, both of Houston, face charges for allegedly distributing controlled substances through Relief Medical Center and GroveCare clinics."

**Cached File:** `/Users/chiho/ai-lab/CardioGuard_AI/data/cache/web_search/search_CARLOS_MUNOZ_1386756476_Internal_Medicine__Endocri.json`

---

## Extraction Process

### Step 1: Web Search Discovery
1. **ResearchAgent** calls `WebSearchService.search_provider_legal_info()`
2. Searches for "CARLOS MUNOZ" with healthcare fraud keywords
3. Returns 16 search results from DuckDuckGo
4. Results cached for 30 days

### Step 2: Legal Information Parsing
1. **LegalParserService** processes search results
2. Classifies result #1 as: `case_type="allegation"`, `status="pending"`
3. Extracts description: "Allegation (pending): Houston health care fraud takedown targets $110 million scheme"
4. Relevance score: 0.30 (passed threshold)

### Step 3: Financial Data Extraction
1. **LegalParserService.extract_fraud_financial_data()** called
2. Regex pattern matches: `r'\$[\d,]+\.?\d*\s*(million|billion|m|b|M|B)\b'`
3. Matches "$110 million" in article title
4. Parses to: `110 × 1,000,000 = $110,000,000.00`
5. Context analysis: Keyword "fraud" in title → classified as `estimated_fraud_amount`

### Step 4: Financial Data Storage
1. **DataService._extract_and_save_fraud_financial_data()** aggregates amounts
2. Saves to `FraudFinancialService` (JSON storage)
3. Stored in: `data/fraud_financial/fraud_financial_data.json`
4. Record includes:
   - `estimated_fraud_amount`: 110000000.0
   - `source`: "Public records"
   - `notes`: "Estimated fraud: $110,000,000"

---

## Risk Score Contribution

### Current Implementation

**Financial Data Status:** Extracted ✅ | Stored ✅ | **Used in Risk Score: ❌**

**How Legal Issues Contribute:**
- The allegation containing the $110M fraud was classified as 1 of 4 allegations
- Allegations contribute **+10 points each** to risk score
- **Total from this allegation:** +10 points (not +110M points)

**Financial Amount Impact:**
- The $110,000,000 amount itself does **NOT** add additional risk points
- Financial data is extracted and displayed for informational purposes
- Currently used only for reporting/display, not scoring

### Risk Score Breakdown

**Legal Information Scoring:**
- 3 pending lawsuits × 15 points = **45 points**
- 4 allegations × 10 points = **40 points**
  - Includes allegation #6: "Houston health care fraud takedown targets $110 million scheme" = **+10 points**
- **Total legal points:** 85 points

**Financial Data Scoring:**
- **$110M fraud amount:** **+0 points** (not factored into calculation)
- Financial data is informational only

**Final Risk Score:** 85/100 (from legal issues, not financial amount)

---

## Why Financial Data Isn't Used in Scoring

### Current Design Decision

The risk scoring algorithm focuses on:
1. **Legal case types** (conviction, lawsuit, allegation)
2. **Case status** (pending, settled, closed)
3. **Number of legal issues** (multiple issues = higher risk)

Financial amounts are:
- Extracted for **reporting and context**
- Displayed to show **severity of fraud**
- **Not used** in numerical risk calculation

### Potential Enhancement

To factor financial impact into risk score, could add:
- **Financial impact multiplier:** Scale risk score based on fraud amount
  - Example: $110M fraud could add +5 to +15 additional points
- **Tiered financial scoring:**
  - $0-$1M: +0 points
  - $1M-$10M: +5 points
  - $10M-$100M: +10 points
  - $100M+: +15 points

**Current Status:** Not implemented - financial data is informational only

---

## Data Flow Summary

```
Web Search (DuckDuckGo)
    ↓
Search Results (16 results)
    ↓
Legal Parser Service
    ↓
Legal Information (7 items parsed)
    ↓
Financial Data Extractor
    ↓
Fraud Financial Service (JSON storage)
    ↓
Risk Score Calculator
    ↓
[Financial data NOT used - only legal case types scored]
```

---

## Conclusion

The **$110,000,000 fraud amount** was successfully extracted from **Web Search** results (specifically a news article), but it currently **does NOT contribute to the risk score calculation**. The risk score of 85/100 comes entirely from:
- 3 lawsuits (45 points)
- 4 allegations (40 points) - one of which mentions the $110M fraud

The financial amount is stored and displayed for context but does not add additional numerical risk points beyond the legal case type scoring.
