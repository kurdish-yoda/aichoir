"""
Court record scrapers package.

Plugin-ready library for searching public court records across multiple
jurisdictions. Each scraper can be imported independently.

Usage:
    # Search all jurisdictions
    from scrapers import SearchCriteria, search_court_records, get_api_response
    criteria = SearchCriteria(first_name="John", last_name="Doe")
    cases = search_court_records(criteria)
    response = get_api_response(cases, criteria)

    # Use a single scraper
    from scrapers.miami_dade import MiamiDadeScraper
    scraper = MiamiDadeScraper()
    cases = scraper.search(criteria)
"""

import time

from .base import (
    SearchCriteria,
    CourtCase,
    ScraperError,
    CountyScraper,
    CASE_AGE_LIMIT_YEARS,
    EXCLUDED_CASE_TYPES,
)
from .miami_dade import MiamiDadeScraper
from .broward import BrowardScraper
from .new_york import NewYorkScraper

__all__ = [
    # Data models
    "SearchCriteria",
    "CourtCase",
    "ScraperError",
    "CountyScraper",
    # Scrapers
    "MiamiDadeScraper",
    "BrowardScraper",
    "NewYorkScraper",
    # Registry & helpers
    "COUNTY_SCRAPERS",
    "get_scraper",
    "get_all_scrapers",
    "search_court_records",
    "get_api_response",
    # Constants
    "CASE_AGE_LIMIT_YEARS",
    "EXCLUDED_CASE_TYPES",
]

# Registry mapping county names to their scraper classes
COUNTY_SCRAPERS: dict[str, type[CountyScraper]] = {
    "miami-dade": MiamiDadeScraper,
    "broward": BrowardScraper,
    "new-york": NewYorkScraper,
}


def get_scraper(county: str) -> CountyScraper:
    """
    Factory function to get the appropriate scraper for a county.

    Args:
        county: County name (case-insensitive)

    Returns:
        Instance of the appropriate CountyScraper subclass

    Raises:
        ValueError: If no scraper exists for the specified county
    """
    county_key = county.lower().strip()

    if county_key not in COUNTY_SCRAPERS:
        available = ", ".join(COUNTY_SCRAPERS.keys())
        raise ValueError(
            f"No scraper available for '{county}'. "
            f"Available counties: {available}"
        )

    return COUNTY_SCRAPERS[county_key]()


def get_all_scrapers() -> list[CountyScraper]:
    """
    Get instances of all available county scrapers.

    Returns:
        List of CountyScraper instances
    """
    scrapers = []
    for scraper_class in COUNTY_SCRAPERS.values():
        try:
            scrapers.append(scraper_class())
        except Exception:
            pass  # Skip scrapers that fail to initialize
    return scrapers


def search_court_records(criteria: SearchCriteria) -> list[CourtCase]:
    """
    Execute court records search based on provided criteria.

    Args:
        criteria: SearchCriteria with search parameters

    Returns:
        Combined list of CourtCase objects from all searched counties
    """
    all_cases = []

    if criteria.county:
        # Search specific county
        print(f"\nSearching {criteria.county} County...")
        try:
            scraper = get_scraper(criteria.county)
            cases = scraper.search(criteria)
            all_cases.extend(cases)
            print(f"  Found {len(cases)} case(s) in {scraper.county_name}")
        except ValueError as e:
            print(f"  Error: {e}")
        except ScraperError as e:
            print(f"  Search error: {e}")
        except NotImplementedError as e:
            print(f"  {e}")
    else:
        # Statewide search - query all available counties
        print("\nPerforming statewide search...")
        print("(Note: Currently limited to implemented county scrapers)")

        for county_name, scraper_class in COUNTY_SCRAPERS.items():
            try:
                print(f"\n  Searching {county_name.title()} County...")
                scraper = scraper_class()
                cases = scraper.search(criteria)
                all_cases.extend(cases)
                print(f"    Found {len(cases)} case(s)")

                # Delay between counties
                time.sleep(2)
            except NotImplementedError:
                print(f"    Skipped - scraper not yet implemented")
            except ScraperError as e:
                print(f"    Search error: {e}")
            except Exception as e:
                print(f"    Unexpected error: {e}")

    return all_cases


def get_api_response(cases: list[CourtCase], criteria: SearchCriteria) -> dict:
    """
    Return search results in API-friendly JSON format for frontend consumption.

    Returns comprehensive case details including all scraped information,
    search URL, and verification instructions.

    Args:
        cases: List of CourtCase objects
        criteria: Original search criteria

    Returns:
        Dictionary containing search results and metadata
    """
    # Count open vs closed cases
    open_cases = [c for c in cases if c.status.upper() in ("OPEN", "ACTIVE", "PENDING")]
    closed_cases = [c for c in cases if c not in open_cases]

    # Convert cases to dictionaries
    case_data = []
    for case in cases:
        case_dict = {
            "case_number": case.case_number,
            "case_type": case.case_type,
            "filing_date": case.filing_date,
            "status": case.status,
            "county": case.county,
            "parties": case.parties,
            "court_division": case.court_division,
            "judge": case.judge,
            "amount": case.amount,
            "disposition_date": case.disposition_date,
            "section": case.section,
            "verification_instructions": case.verification_instructions,
            "search_results_url": case.search_results_url,
        }
        case_data.append(case_dict)

    # Determine which counties were actually searched
    if criteria.county:
        searched_counties = [criteria.county.title()]
    else:
        # Statewide search - all available counties
        searched_counties = ["Miami-Dade", "Broward", "New York"]

    response = {
        "search_criteria": {
            "first_name": criteria.first_name,
            "last_name": criteria.last_name,
            "middle_name": criteria.middle_name,
            "date_of_birth": criteria.date_of_birth,
            "county": criteria.county,
            "search_period_years": CASE_AGE_LIMIT_YEARS,
        },
        "summary": {
            "total_cases": len(cases),
            "open_cases": len(open_cases),
            "closed_cases": len(closed_cases),
            "has_open_cases": len(open_cases) > 0,
        },
        "cases": case_data,
        "metadata": {
            "searched_counties": searched_counties,
            "exclusions": list(EXCLUDED_CASE_TYPES),
            "note": "Results are for preliminary due diligence only. Always verify with official court records.",
            "official_verification_url": "https://www.myflcourtaccess.com",
        }
    }

    return response
