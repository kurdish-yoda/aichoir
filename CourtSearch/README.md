# CourtSearch

Automated court record lookup for lending due diligence. Scrapes public court record portals across multiple jurisdictions, filters for financially relevant civil cases, and returns structured data for both CLI display and API consumption.

All searches are conducted on publicly available records with the borrower's informed consent.

## What It Searches For

- Civil lawsuits (debt collection, contract disputes)
- Foreclosures
- Judgments and liens
- Small claims
- Probate (creditor claims)

## What It Excludes

Criminal cases, family court, traffic violations, and anything older than 5 years.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

Optional (improves New York Cloudflare bypass):
```bash
pip install playwright-stealth
```

## Usage

### CLI (interactive)

```bash
python court_lookup.py
```

Prompts for first name, last name, optional middle name and DOB. Searches all available jurisdictions automatically.

### As a Library (for backend integration)

```python
from scrapers import SearchCriteria, search_court_records, get_api_response

criteria = SearchCriteria(
    first_name="John",
    last_name="Doe",
    middle_name="Q",              # optional
    date_of_birth="01/01/1980",   # optional, MM/DD/YYYY
)

# Search all jurisdictions
cases = search_court_records(criteria)

# Get JSON-serializable API response
response = get_api_response(cases, criteria)
```

### Single Scraper (one jurisdiction)

```python
from scrapers import SearchCriteria
from scrapers.miami_dade import MiamiDadeScraper

scraper = MiamiDadeScraper()
cases = scraper.search(SearchCriteria(first_name="John", last_name="Doe"))
```

## Supported Jurisdictions

| County | Scraper | Portal | Notes |
|--------|---------|--------|-------|
| Miami-Dade | `MiamiDadeScraper` | [OCS Portal](https://www2.miamidadeclerk.gov/ocs/) | Playwright, SPA card parsing |
| Broward | `BrowardScraper` | [Clerk Portal](https://www.browardclerk.org/Web2/) | Subscriber login, Kendo grid |
| New York (statewide) | `NewYorkScraper` | [NYSCEF](https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name) | Async Playwright, stealth mode |

## Project Structure

```
CourtSearch/
├── scrapers/              # Core library
│   ├── __init__.py        # Public API, scraper registry, search_court_records()
│   ├── base.py            # Shared: ABC, dataclasses, filter/sort logic
│   ├── miami_dade.py      # Miami-Dade County scraper
│   ├── broward.py         # Broward County scraper
│   └── new_york.py        # New York State scraper
├── court_lookup.py        # CLI entrypoint
├── requirements.txt       # Dependencies
└── CLAUDE.md              # AI assistant context
```

**Why `__init__.py`?** Required by Python to make `scrapers/` an importable package. Also holds the registry (`COUNTY_SCRAPERS`) and convenience functions (`search_court_records`, `get_api_response`).

**Why `base.py`?** Shared code inherited by all scrapers: the abstract base class, `SearchCriteria`/`CourtCase` dataclasses, and the `_filter_and_sort_cases()` method (previously duplicated 3x across each scraper).

## API Response Format

```json
{
  "search_criteria": {
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "Q",
    "date_of_birth": "01/01/1980",
    "county": null,
    "search_period_years": 5
  },
  "summary": {
    "total_cases": 3,
    "open_cases": 2,
    "closed_cases": 1,
    "has_open_cases": true
  },
  "cases": [
    {
      "case_number": "2024-CA-012345",
      "case_type": "Civil",
      "filing_date": "01/15/2024",
      "status": "Open",
      "county": "Miami-Dade",
      "parties": "John Q. Doe vs. ABC Corporation",
      "court_division": "Civil Division 1",
      "judge": "Hon. Jane Smith",
      "amount": "$25,000.00",
      "disposition_date": "",
      "section": "CA06 - Downtown Miami",
      "verification_instructions": "...",
      "search_results_url": "https://www2.miamidadeclerk.gov/ocs/"
    }
  ],
  "metadata": {
    "searched_counties": ["Miami-Dade", "Broward", "New York"],
    "exclusions": ["Family", "Criminal", "Criminal Felony", "Criminal Misdemeanor", "Traffic"],
    "note": "Results are for preliminary due diligence only...",
    "official_verification_url": "https://www.myflcourtaccess.com"
  }
}
```

## Adding a New Jurisdiction

1. Create `scrapers/your_county.py`:

```python
from .base import CountyScraper, SearchCriteria, CourtCase

class YourCountyScraper(CountyScraper):
    @property
    def county_name(self) -> str:
        return "Your County"

    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        cases = self._your_search_logic(criteria)
        return self._filter_and_sort_cases(cases, criteria)
```

2. Register in `scrapers/__init__.py`:

```python
from .your_county import YourCountyScraper
COUNTY_SCRAPERS["your-county"] = YourCountyScraper
```

That's it. The new scraper is immediately available through `search_court_records()` and the CLI.

## Known Limitations

- **Broward CAPTCHA**: Subscriber login helps but CAPTCHAs can still appear. Fails gracefully with manual search instructions.
- **NY Cloudflare**: Turnstile challenge frequently blocks automated access. Stealth mode + retries with backoff help but don't guarantee success.
- **Brittle selectors**: Court sites change HTML without notice. Scrapers use multi-selector fallbacks but periodic maintenance is expected.
- **No caching**: Every search hits live portals. Repeated searches on the same person waste time and risk rate limiting.
- **Name disambiguation**: Common names return many results. Provide middle name and DOB for better filtering.
