Court Records Lookup - Project Documentation
Overview
This project is an internal tool for lending due diligence. It automates the lookup of public court records to identify civil/financial cases associated with a loan applicant. All searches are conducted with the client's informed consent.

The script scrapes publicly available court record portals across multiple jurisdictions, filters results for lending relevance, and returns structured data suitable for both CLI display and API consumption.

Purpose & Business Context
When evaluating a loan application, the lending team needs to know if the applicant has:

Open civil lawsuits (current legal exposure / financial risk)
Judgments or liens against them
Foreclosure history
Debt collection actions
Contract disputes
Small claims filings
This tool automates what would otherwise be a tedious, manual process of visiting multiple county court websites and searching one by one.

What We Exclude (Not Relevant for Lending)
Excluded Category	Reason
Criminal cases	Not part of financial due diligence
Family court (divorce, custody)	Not relevant to creditworthiness
Traffic violations	Not relevant
Cases older than 5 years	Stale data, limited predictive value
Architecture
High-Level Flow
text

User Input (name, optional DOB/middle name)
    │
    ▼
SearchCriteria dataclass
    │
    ▼
Scraper Registry (factory pattern)
    │
    ├── MiamiDadeScraper
    ├── BrowardScraper
    └── NewYorkScraper
    │
    ▼
Each scraper:
  1. Launches headless Chromium via Playwright
  2. Navigates to court portal
  3. Fills search form programmatically
  4. Waits for SPA to render results
  5. Parses HTML into CourtCase objects
    │
    ▼
Filter & Sort Pipeline
  - Remove excluded case types
  - Remove cases > 5 years old
  - Verify name matching (last name required, first name flexible)
  - Sort: Open cases first, then newest first
    │
    ▼
Output
  - CLI: formatted table with details
  - API: structured dict (JSON-serializable)
Key Design Decisions
Abstract base class (CountyScraper): Each jurisdiction has a wildly different website. The ABC enforces a consistent interface (search(), county_name) while allowing each scraper to handle its own HTML structure.
Playwright over plain requests: Most court portals are JavaScript SPAs. Static HTTP requests return empty shells. Playwright renders the full page.
Factory pattern via COUNTY_SCRAPERS registry: Adding a new county means writing a new scraper class and adding one line to the registry dict.
Aggressive filtering post-scrape: Court searches return broad results. We filter heavily on case type, date range, and name matching to reduce false positives.
Data Models
SearchCriteria
Python

@dataclass
class SearchCriteria:
    first_name: str          # Required
    last_name: str           # Required
    middle_name: str | None  # Helps disambiguate common names
    date_of_birth: str | None  # MM/DD/YYYY format, used if portal supports it
    county: str | None       # None = search all available jurisdictions
CourtCase
Python

@dataclass
class CourtCase:
    case_number: str                # Unique case ID (e.g., "2024-CA-012345")
    case_type: str                  # Civil, Small Claims, Foreclosure, etc.
    filing_date: str                # When the case was filed
    status: str                     # Open, Closed, Pending, Unknown
    county: str                     # Jurisdiction
    parties: str                    # Full party names (plaintiff vs defendant)
    court_division: str             # Division handling the case
    judge: str                      # Assigned judge
    amount: str                     # Monetary amount if available
    disposition_date: str           # When case was closed (if closed)
    section: str                    # Court section/location
    verification_instructions: str  # How to manually verify this case
    search_results_url: str         # URL to the search portal
Supported Jurisdictions
Miami-Dade County (Florida)
Detail	Value
Scraper class	MiamiDadeScraper
Portal	https://www2.miamidadeclerk.gov/ocs/
Method	Playwright → click "Party Name" nav → fill form → parse TitleSearchTab cards
Case type detection	Uses case type codes (CA=Civil, FA=Family, PR=Probate, CF=Criminal Felony, etc.)
Known issues	May require CAPTCHA for heavy usage; registration recommended
HTML parsing specifics: Results appear as div.TitleSearchTab cards with data-id attributes for field labels (e.g., <p data-id="Local Case Number">2024-CA-012345</p>). Parties are in p.fw-bold elements.

Broward County (Florida)
Detail	Value
Scraper class	BrowardScraper
Portal	https://www.browardclerk.org/web2/
Method	Playwright → navigate to search → find Party Name tab → fill form
Known issues	CAPTCHA-protected — automated search frequently blocked
CAPTCHA handling: The scraper detects CAPTCHA presence (reCAPTCHA, hCAPTCHA, "I'm not a robot" text) and gracefully fails with manual search instructions rather than hanging. This is by design — we cannot and should not bypass CAPTCHAs.

Form detection: Broward's form structure is unpredictable. The scraper uses a multi-stage fallback:

Try standard selectors (#partyFirstName, etc.)
Scan all inputs for name-related attributes
Emergency mode: use first two visible text inputs
If all fail, print manual instructions and move on
New York State
Detail	Value
Scraper class	NewYorkScraper
Portal	https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name
Method	Playwright → fill name fields → submit → parse table/container results
Scope	Statewide (NYSCEF covers all NY counties)
Case type detection	Keyword-based classification (Commercial, Contract, Insurance, Debt Collection, Real Estate, etc.)
Filtering & Sorting Logic
Name Matching
The filter is deliberately strict on last name, flexible on first name:

Last name: Must appear in the parties text (required, no exceptions)
First name: Checked with fallbacks:
Exact match in parties text
First initial + period + last name (e.g., "J. Smith")
First initial + space + last name (e.g., "J Smith")
Middle name: If provided, can substitute for first name match
Logic: Keep case if last_name_matches AND (first_name_matches OR middle_name_matches)

Date Filtering
Cases older than CASE_AGE_LIMIT_YEARS (currently 5) are excluded
Cases with unparseable dates are kept (fail-open to avoid missing relevant records)
Date parsing uses python-dateutil for flexible format handling
Sort Order
Open/Active/Pending cases first — these represent current legal exposure
Within each status group, newest first — most recent filings are most relevant
Dependencies
text

requests          # HTTP client for basic page fetches
beautifulsoup4    # HTML parsing (with lxml parser)
lxml              # Fast HTML/XML parser backend for BeautifulSoup
playwright        # Headless browser for JavaScript-rendered SPAs
tabulate          # CLI table formatting
python-dateutil   # Flexible date parsing
Playwright Setup
Playwright requires a separate browser installation step:

Bash

pip install playwright
playwright install chromium
If Playwright is not installed, the scrapers will print an error and return empty results (graceful degradation, not a crash).

Entry Points
CLI Usage
Bash

python court_lookup.py
Interactive prompts for:

First name (required)
Last name (required)
Middle name (optional)
Date of birth in MM/DD/YYYY (optional)
Automatically searches all available jurisdictions (no county selection needed).

Programmatic Usage
Python

from court_lookup import SearchCriteria, search_court_records, get_api_response

criteria = SearchCriteria(
    first_name="John",
    last_name="Doe",
    middle_name="Q",
    date_of_birth="01/01/1980",
    county=None  # None = search all jurisdictions
)

cases = search_court_records(criteria)
api_response = get_api_response(cases, criteria)  # Returns JSON-serializable dict
API Response Format
JSON

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
Test Functions
Function	Purpose
test_api_response()	Demonstrates API response format with sample data (no network calls)
test_scraper_initialization()	Verifies all scrapers can be instantiated
test_ny_scraper_basic()	Verifies NY scraper setup without network access
Adding a New Jurisdiction
Create a new scraper class inheriting from CountyScraper:
Python

class PalmBeachScraper(CountyScraper):
    @property
    def county_name(self) -> str:
        return "Palm Beach"

    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        # Implement search logic
        pass
Register it in the COUNTY_SCRAPERS dict:
Python

COUNTY_SCRAPERS: dict[str, type[CountyScraper]] = {
    "miami-dade": MiamiDadeScraper,
    "broward": BrowardScraper,
    "new-york": NewYorkScraper,
    "palm-beach": PalmBeachScraper,  # Add this line
}
Key things to implement:
Figure out the court portal's HTML structure (use browser DevTools)
Determine if Playwright is needed (most SPAs require it)
Implement name matching and case type classification for that jurisdiction
Reuse _filter_and_sort_cases() logic (it's duplicated across scrapers currently — see Known Issues)
Configuration
Constant	Value	Location	Purpose
CASE_AGE_LIMIT_YEARS	5	Module level	How far back to include cases
EXCLUDED_CASE_TYPES	{"Family", "Criminal", ...}	Module level	Case types to filter out
REQUEST_DELAY	1.5 seconds	CountyScraper class	Delay between HTTP requests
DEFAULT_HEADERS	Chrome UA string	CountyScraper class	Browser impersonation headers
Known Issues & Technical Debt
CAPTCHA Blocking
Broward County (and potentially others) use CAPTCHA protection. The scraper cannot bypass this and is designed to fail gracefully with manual instructions. This is a fundamental limitation of automated scraping.

Code Duplication
_filter_and_sort_cases() is copy-pasted identically across MiamiDadeScraper, BrowardScraper, and NewYorkScraper. This should be refactored into the CountyScraper base class.

Rate Limiting
The scrapers include a 1.5-second delay between requests and a 2-second delay between counties, but aggressive use could still trigger rate limiting or IP bans on court portals.

Name Disambiguation
Common names (e.g., "John Smith") will return many results. The filter helps but cannot guarantee identity matching. DOB filtering depends on the portal supporting it — not all do.

DOB Input Bug
In get_user_input(), there is a bug where dob is unconditionally set to None after validation due to an incorrectly placed dob = None statement at the end of the validation block. DOB will never actually be passed to the search criteria from CLI input.

Brittle Selectors
Court websites change their HTML structure without notice. Selectors (CSS selectors, class names, IDs) will break when this happens. Each scraper uses multiple fallback selectors to mitigate this, but periodic maintenance is expected.

No Caching
Every search hits the court portals live. There is no caching layer. For repeated searches on the same person, this wastes time and increases rate-limiting risk.

Legal & Compliance Notes
All searches are on publicly available court records
Searches are conducted with the borrower's informed consent
Results are for preliminary due diligence only — not a substitute for official record verification
The tool does not access criminal records, sealed records, or non-public data
A disclaimer is displayed after every CLI search
