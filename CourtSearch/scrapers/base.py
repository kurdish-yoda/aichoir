"""
Base classes, data models, and shared utilities for court record scrapers.

This module contains:
- SearchCriteria and CourtCase dataclasses
- CountyScraper abstract base class with shared filtering logic
- ScraperError exception
- Configuration constants
"""

import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

# Configuration: How many years back to include cases
CASE_AGE_LIMIT_YEARS = 5

# Case types to EXCLUDE (not relevant for lending due diligence)
EXCLUDED_CASE_TYPES = {"Family", "Criminal", "Criminal Felony", "Criminal Misdemeanor", "Traffic"}

# Attempt to import playwright - only needed if JS rendering required
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class SearchCriteria:
    """
    Data class to hold search parameters for court record lookups.

    Attributes:
        first_name: Person's first name (required)
        last_name: Person's last name (required)
        middle_name: Person's middle name (optional)
        date_of_birth: Date of birth in MM/DD/YYYY format (optional)
        county: Florida county name (optional - None means statewide)
    """
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    county: Optional[str] = None


@dataclass
class CourtCase:
    """
    Data class representing a single court case record.

    Attributes:
        case_number: Unique identifier for the case
        case_type: Type of case (Civil, Criminal, Family, etc.)
        filing_date: Date the case was filed
        status: Current status (Open/Closed/Pending)
        county: County where case was filed
        parties: String describing parties involved
        court_division: Division of court handling the case
        judge: Name of the judge assigned to the case
        amount: Monetary amount involved in the case (if available)
        disposition_date: Date the case was disposed/closed
        section: Court section/location information
        verification_instructions: Instructions for manual verification
        search_results_url: URL to view all search results
    """
    case_number: str
    case_type: str
    filing_date: str
    status: str
    county: str
    parties: str
    court_division: str = ""
    judge: str = ""
    amount: str = ""
    disposition_date: str = ""
    section: str = ""
    verification_instructions: str = ""
    search_results_url: str = ""


# ==============================================================================
# BASE SCRAPER CLASS
# ==============================================================================

class CountyScraper(ABC):
    """
    Abstract base class for county-specific court record scrapers.

    Each county may have a different website structure, so this provides
    a common interface that all county scrapers must implement.

    Subclasses must implement:
        - search(): Performs the actual search and returns results
        - county_name: Property returning the county name
    """

    # Standard headers to mimic a real browser
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Delay between requests to avoid rate limiting (seconds)
    REQUEST_DELAY = 1.5

    def __init__(self):
        """Initialize the scraper with a requests session."""
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    @property
    @abstractmethod
    def county_name(self) -> str:
        """Return the name of the county this scraper handles."""
        pass

    @abstractmethod
    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search court records based on the given criteria.

        Args:
            criteria: SearchCriteria object with search parameters

        Returns:
            List of CourtCase objects matching the search

        Raises:
            ScraperError: If the search fails due to site issues
        """
        pass

    def _delay(self):
        """Add a delay between requests to avoid rate limiting."""
        time.sleep(self.REQUEST_DELAY)

    def _get_page(self, url: str, params: dict = None) -> BeautifulSoup:
        """
        Fetch a page and return parsed BeautifulSoup object.

        Args:
            url: URL to fetch
            params: Optional query parameters

        Returns:
            BeautifulSoup object of the page content

        Raises:
            ScraperError: If the request fails
        """
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            raise ScraperError(f"Failed to fetch {url}: {e}")

    def _post_page(self, url: str, data: dict = None) -> BeautifulSoup:
        """
        Submit a POST request and return parsed BeautifulSoup object.

        Args:
            url: URL to post to
            data: Form data to submit

        Returns:
            BeautifulSoup object of the response content

        Raises:
            ScraperError: If the request fails
        """
        try:
            response = self.session.post(url, data=data, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            raise ScraperError(f"Failed to post to {url}: {e}")

    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace and clean text."""
        return " ".join(text.split()).strip()

    def _filter_and_sort_cases(self, cases: list[CourtCase], criteria: SearchCriteria = None) -> list[CourtCase]:
        """
        Filter and sort cases for lending due diligence relevance.

        Filtering:
        - Remove excluded case types (Family, Criminal, Traffic)
        - Remove cases older than 5 years
        - Filter by party name matching if criteria provided

        Sorting:
        - Open/Active cases first (current legal exposure)
        - Then by filing date (most recent first)

        Args:
            cases: Raw list of CourtCase objects
            criteria: Search criteria for additional filtering

        Returns:
            Filtered and sorted list of CourtCase objects
        """
        cutoff_date = datetime.now() - timedelta(days=CASE_AGE_LIMIT_YEARS * 365)
        filtered = []

        for case in cases:
            # Skip excluded case types
            if case.case_type in EXCLUDED_CASE_TYPES:
                continue

            # Parse and check filing date
            try:
                if case.filing_date and case.filing_date != "N/A":
                    case_date = date_parser.parse(case.filing_date)
                    if case_date < cutoff_date:
                        continue  # Skip cases older than 5 years
            except (ValueError, TypeError):
                pass  # Keep cases with unparseable dates

            # Additional filtering: check if party names contain search terms
            if criteria:
                party_text = case.parties.lower() if case.parties else ""

                # Require last name to appear
                last_in_party = criteria.last_name.lower() in party_text
                if not last_in_party:
                    continue

                # For first name, be more flexible - check for first name OR common variations
                first_name_lower = criteria.first_name.lower()
                first_in_party = first_name_lower in party_text

                # Also check for common abbreviations or partial matches
                if not first_in_party:
                    # Check for first initial + last name pattern (e.g., "A. Smith")
                    if len(first_name_lower) > 0:
                        initial_pattern = f"{first_name_lower[0]}\. {criteria.last_name.lower()}"
                        if initial_pattern in party_text:
                            first_in_party = True

                        # Check for first initial without dot (e.g., "A Smith")
                        initial_pattern2 = f"{first_name_lower[0]} {criteria.last_name.lower()}"
                        if initial_pattern2 in party_text:
                            first_in_party = True

                # If we have a middle name, check if it appears
                middle_in_party = False
                if criteria.middle_name:
                    middle_in_party = criteria.middle_name.lower() in party_text

                # Keep case if: last name appears AND (first name appears OR middle name appears)
                # This is stricter than before but still allows for name variations
                if not (last_in_party and (first_in_party or middle_in_party)):
                    continue

            filtered.append(case)

        # Sort: Open cases first, then by date (newest first)
        def sort_key(case: CourtCase):
            # Priority 1: Open cases come first (0), Closed cases after (1)
            status_priority = 0 if case.status.upper() in ("OPEN", "ACTIVE", "PENDING") else 1

            # Priority 2: Date (newest first, so negate timestamp)
            try:
                if case.filing_date and case.filing_date != "N/A":
                    case_date = date_parser.parse(case.filing_date)
                    date_score = -case_date.timestamp()
                else:
                    date_score = 0
            except (ValueError, TypeError):
                date_score = 0

            return (status_priority, date_score)

        filtered.sort(key=sort_key)

        return filtered


class ScraperError(Exception):
    """Custom exception for scraper-related errors."""
    pass
