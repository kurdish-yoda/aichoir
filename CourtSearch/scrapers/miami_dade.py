"""
Miami-Dade County court record scraper.

Searches the Miami-Dade Clerk OCS portal for civil/financial cases.
Website: https://www2.miamidadeclerk.gov/ocs/
"""

import re
import time
from typing import Optional

from bs4 import BeautifulSoup

from .base import (
    CountyScraper,
    SearchCriteria,
    CourtCase,
    ScraperError,
    PLAYWRIGHT_AVAILABLE,
)

if PLAYWRIGHT_AVAILABLE:
    from playwright.sync_api import sync_playwright


class MiamiDadeScraper(CountyScraper):
    """
    Scraper for Miami-Dade County Clerk court records.

    Focused on civil/financial cases for lending due diligence:
    - Civil lawsuits, foreclosures, judgments
    - Small claims
    - Probate (creditor claims only)

    Excludes: Criminal cases, Family court (not relevant for lending)

    Website: https://www.miamidadeclerk.gov/
    Search Portal: https://www2.miamidadeclerk.gov/ocs/
    """

    # Base URL for Miami-Dade Clerk civil records
    BASE_URL = "https://www2.miamidadeclerk.gov"
    CIVIL_SEARCH_URL = f"{BASE_URL}/ocs/"  # Civil, Probate, Small Claims

    @property
    def county_name(self) -> str:
        return "Miami-Dade"

    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search Miami-Dade civil court records by party name.

        Searches the OCS (Official Court System) for civil, probate, and
        small claims cases. Results are filtered to:
        - Exclude family/criminal cases
        - Only include cases from last 5 years
        - Sort by status (Open first) then date (newest first)

        Args:
            criteria: SearchCriteria with at minimum first_name and last_name

        Returns:
            List of CourtCase objects from Miami-Dade County (filtered & sorted)
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("  Error: Playwright is required for Miami-Dade searches.")
            print("  Install with: pip install playwright && playwright install chromium")
            return []

        # Search civil records only (no criminal - not relevant for lending)
        print("    Searching Civil court records...")
        cases = self._search_civil_records(criteria)

        # Filter and sort results for lending relevance
        filtered_cases = self._filter_and_sort_cases(cases, criteria)

        print(f"      Found {len(filtered_cases)} relevant case(s) (after filtering)")

        return filtered_cases

    def _search_civil_records(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search civil and probate records via the OCS portal.

        Args:
            criteria: Search parameters

        Returns:
            List of CourtCase objects from civil courts
        """
        return self._search_with_playwright(
            url=self.CIVIL_SEARCH_URL,
            criteria=criteria,
            case_type_default="Civil"
        )

    def _search_with_playwright(
        self,
        url: str,
        criteria: SearchCriteria,
        case_type_default: str
    ) -> list[CourtCase]:
        """
        Execute search using Playwright for JavaScript-rendered SPA content.

        Miami-Dade OCS/CJIS requires navigation through a menu to reach the
        search form (Party Name search). This method:
        1. Navigates to the portal home
        2. Clicks the "Party Name" link in the navigation menu
        3. Fills in the search form
        4. Parses the results

        Args:
            url: URL of the search portal
            criteria: Search parameters
            case_type_default: Default case type if not detected

        Returns:
            List of CourtCase objects
        """
        cases = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=self.DEFAULT_HEADERS["User-Agent"]
            )
            page = context.new_page()

            try:
                # Navigate to portal home and wait for SPA to load
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(3)  # Allow SPA to fully initialize

                # Navigate to Party Name search page
                nav_selectors = [
                    "span:has-text('Party Name')",
                    "[role='button']:has-text('Party Name')",
                    "span.cursorPointer:has-text('Party')",
                    "a:has-text('Party Name')",
                ]

                clicked = False
                for selector in nav_selectors:
                    try:
                        loc = page.locator(selector)
                        if loc.count() > 0:
                            loc.first.click()
                            page.wait_for_load_state("networkidle", timeout=30000)
                            time.sleep(3)
                            clicked = True
                            break
                    except Exception:
                        continue

                if not clicked:
                    print(f"      Could not find Party Name search link at {url}")
                    return []

                # Now fill the search form
                filled_form = self._fill_search_form(page, criteria)

                if not filled_form:
                    print(f"      Could not find search form fields")
                    return []

                # Submit the search
                self._submit_search(page)

                # Wait for results to load
                time.sleep(4)
                page.wait_for_load_state("networkidle", timeout=30000)

                # Parse results from rendered page
                content = page.content()
                cases = self._parse_spa_results(content, case_type_default)

                # Only warn about CAPTCHA if no results were found
                if not cases and self._has_captcha(page):
                    print("      Note: CAPTCHA may be blocking results")
                    print("      Consider registering at the site for unlimited searches")

            except Exception as e:
                print(f"      Search error: {e}")
            finally:
                browser.close()

        return cases

    def _has_captcha(self, page) -> bool:
        """
        Check if the page contains a CAPTCHA challenge.

        Args:
            page: Playwright page object

        Returns:
            True if CAPTCHA is detected
        """
        captcha_indicators = [
            "iframe[src*='recaptcha']",
            "iframe[src*='captcha']",
            ".g-recaptcha",
            "#recaptcha",
            "div[class*='captcha']",
        ]

        for selector in captcha_indicators:
            try:
                if page.locator(selector).count() > 0:
                    return True
            except Exception:
                pass

        return False

    def _fill_search_form(self, page, criteria: SearchCriteria) -> bool:
        """
        Fill in the search form fields for Miami-Dade OCS civil search.

        Args:
            page: Playwright page object
            criteria: Search criteria to fill in

        Returns:
            True if form was successfully filled, False otherwise
        """
        filled_first = False
        filled_last = False

        # OCS civil court form selectors
        first_name_selectors = [
            "#partyFirstName",
            "input[name='partyFirstName']",
            "input[name*='firstName']",
            "input[placeholder*='First']",
        ]

        last_name_selectors = [
            "#partyLastName",
            "input[name='partyLastName']",
            "input[name*='lastName']",
            "input[placeholder*='Last']",
        ]

        # Fill first name
        for selector in first_name_selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible():
                    locator.first.fill(criteria.first_name)
                    filled_first = True
                    break
            except Exception:
                continue

        # Fill last name
        for selector in last_name_selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible():
                    locator.first.fill(criteria.last_name)
                    filled_last = True
                    break
            except Exception:
                continue

        # Optionally fill middle name if available
        if criteria.middle_name:
            middle_selectors = [
                "#partyMiddleName",
                "input[name='partyMiddleName']",
                "input[name*='middleName']",
                "input[placeholder*='Middle']",
            ]
            for selector in middle_selectors:
                try:
                    locator = page.locator(selector)
                    if locator.count() > 0 and locator.first.is_visible():
                        locator.first.fill(criteria.middle_name)
                        break
                except Exception:
                    continue

        # Optionally fill date of birth if available
        if criteria.date_of_birth:
            dob_selectors = [
                "#partyDOB",
                "input[name='partyDOB']",
                "input[name*='DOB']",
                "input[name*='dateOfBirth']",
                "input[placeholder*='DOB']",
                "input[placeholder*='Birth']",
            ]
            for selector in dob_selectors:
                try:
                    locator = page.locator(selector)
                    if locator.count() > 0 and locator.first.is_visible():
                        # Try different date formats
                        locator.first.fill(criteria.date_of_birth)
                        print(f"        Using DOB filter: {criteria.date_of_birth}")
                        break
                except Exception:
                    continue

        return filled_first and filled_last

    def _submit_search(self, page):
        """
        Submit the search form by clicking the search button.

        Tries multiple common button selector patterns.

        Args:
            page: Playwright page object
        """
        submit_selectors = [
            "button:has-text('Search')",
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Find')",
            "button:has-text('Submit')",
            ".search-button",
            "#btnSearch",
        ]

        for selector in submit_selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0:
                    locator.first.click()
                    return
            except Exception:
                continue

        # Fallback: try pressing Enter in the form
        try:
            page.keyboard.press("Enter")
        except Exception:
            pass

    def _parse_spa_results(self, html_content: str, case_type_default: str) -> list[CourtCase]:
        """
        Parse search results from Miami-Dade OCS/CJIS rendered HTML.

        Miami-Dade uses a specific card-based structure with:
        - TitleSearchTab divs containing each result
        - data-id attributes for field labels
        - Parties in p.m-0.fs-5.fw-bold elements

        Args:
            html_content: Full HTML content of the rendered page
            case_type_default: Default case type to use

        Returns:
            List of CourtCase objects extracted from the page
        """
        cases = []
        soup = BeautifulSoup(html_content, "lxml")

        # Miami-Dade specific: Find all TitleSearchTab divs (result cards)
        result_cards = soup.find_all("div", class_=re.compile(r"TitleSearchTab"))

        for card in result_cards:
            case = self._parse_miami_dade_card(card, case_type_default)
            if case:
                cases.append(case)

        # Fallback: Try generic parsing if Miami-Dade structure not found
        if not cases:
            cases = self._parse_generic_results(soup, case_type_default)

        return cases

    def _parse_miami_dade_card(self, card, case_type_default: str) -> Optional[CourtCase]:
        """
        Parse a Miami-Dade OCS result card into a CourtCase object.

        Card structure:
        - Parties in <p class="m-0 fs-5 fw-bold">
        - Case details in <p data-id="Field Name">value</p>

        Extracts all available details including amounts, judge, division, etc.

        Args:
            card: BeautifulSoup element for the result card
            case_type_default: Default case type

        Returns:
            CourtCase object or None if parsing fails
        """
        try:
            # Extract case details using data-id attributes
            def get_field(field_name: str) -> str:
                """Helper to extract field value by data-id."""
                elem = card.find("p", {"data-id": field_name})
                return self._clean_text(elem.get_text()) if elem else ""

            # Get case number (prefer Local Case Number) - REQUIRED
            case_number = get_field("Local Case Number")
            if not case_number:
                case_number = get_field("State Case Number")

            # Skip cards without a valid case number (these are sub-elements)
            if not case_number or case_number == "Unknown":
                return None

            # Extract parties (header of the card)
            parties_elem = card.find("p", class_=re.compile(r"fw-bold"))
            parties = self._clean_text(parties_elem.get_text()) if parties_elem else "Unknown"

            # Get filing date
            filing_date = get_field("Filing Date")
            if not filing_date:
                # Try to find any date pattern in the card
                date_match = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", card.get_text())
                filing_date = date_match.group() if date_match else "N/A"

            # Get case status
            status_text = get_field("Case Status").upper()
            if "CLOSED" in status_text or "DISPOSED" in status_text:
                status = "Closed"
            elif "OPEN" in status_text or "ACTIVE" in status_text or "PENDING" in status_text:
                status = "Open"
            elif status_text:
                status = status_text.title()
            else:
                status = "Unknown"

            # Determine case type from Case Type field or section
            case_type_code = get_field("Case Type")
            section = get_field("Section")
            case_type = self._classify_case_type_from_code(
                case_type_code, section, case_type_default
            )

            # Extract additional comprehensive details
            judge = get_field("Judge")
            court_division = get_field("Division") or section

            # Look for monetary amounts in various fields
            amount = ""
            amount_fields = ["Amount", "Claim Amount", "Judgment Amount", "Damages"]
            for field in amount_fields:
                amt = get_field(field)
                if amt and amt != "N/A" and amt != "":
                    amount = amt
                    break

            # If no specific amount field, look for dollar signs in the card
            if not amount:
                card_text = card.get_text()
                dollar_match = re.search(r'\$[\d,]+\.?\d*', card_text)
                if dollar_match:
                    amount = dollar_match.group()

            # Get disposition date
            disposition_date = get_field("Disposition Date") or get_field("Closed Date")

            # Generate verification instructions
            verification_instructions = (
                f"To verify this case manually: "
                f"1. Visit https://www2.miamidadeclerk.gov/ocs/ "
                f"2. Search for Case Number: {case_number} "
                f"3. Verify all details match your records"
            )

            # Generate search results URL (current search context)
            search_results_url = "https://www2.miamidadeclerk.gov/ocs/"

            return CourtCase(
                case_number=case_number,
                case_type=case_type,
                filing_date=filing_date,
                status=status,
                county="Miami-Dade",
                parties=parties,
                court_division=court_division,
                judge=judge,
                amount=amount,
                disposition_date=disposition_date,
                section=section,
                verification_instructions=verification_instructions,
                search_results_url=search_results_url,
            )
        except Exception:
            return None

    def _classify_case_type_from_code(
        self,
        case_type_code: str,
        section: str,
        default: str
    ) -> str:
        """
        Classify case type from Miami-Dade case type code and section.

        Miami-Dade uses codes like CA (Civil), FA (Family), PR (Probate),
        CF (Criminal Felony), etc.

        Args:
            case_type_code: Case type code (e.g., "CA010", "FA001")
            section: Section info (e.g., "CA06 - Downtown Miami")
            default: Default case type to return

        Returns:
            Human-readable case type string
        """
        code_upper = (case_type_code + section).upper()

        if "CF" in code_upper or "CTC" in code_upper:
            return "Criminal Felony"
        elif "CM" in code_upper or "MM" in code_upper:
            return "Criminal Misdemeanor"
        elif "FA" in code_upper or "DR" in code_upper or "FAMILY" in code_upper:
            return "Family"
        elif "PR" in code_upper or "PROBATE" in code_upper:
            return "Probate"
        elif "CA" in code_upper or "CIVIL" in code_upper:
            return "Civil"
        elif "SC" in code_upper or "SMALL" in code_upper:
            return "Small Claims"
        elif "TR" in code_upper or "TRAFFIC" in code_upper:
            return "Traffic"
        else:
            return default

    def _parse_generic_results(self, soup: BeautifulSoup, case_type_default: str) -> list[CourtCase]:
        """
        Fallback generic parser for non-Miami-Dade structure.

        Args:
            soup: BeautifulSoup object of the page
            case_type_default: Default case type

        Returns:
            List of CourtCase objects
        """
        cases = []

        # Try table-based results
        for table in soup.find_all("table"):
            rows = table.find_all("tr")[1:]  # Skip header
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 3:
                    case = self._parse_table_row(cells, case_type_default)
                    if case:
                        cases.append(case)

        return cases

    def _parse_table_row(self, cells: list, case_type_default: str) -> Optional[CourtCase]:
        """
        Parse a generic table row into a CourtCase object.

        Args:
            cells: List of table cell elements
            case_type_default: Default case type

        Returns:
            CourtCase object or None
        """
        try:
            cell_texts = [self._clean_text(cell.get_text()) for cell in cells]

            if not any(cell_texts):
                return None

            case_number = cell_texts[0] if cell_texts else "Unknown"

            # Find date
            filing_date = "N/A"
            for text in cell_texts:
                date_match = re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", text)
                if date_match:
                    filing_date = date_match.group()
                    break

            # Determine status
            full_text = " ".join(cell_texts).lower()
            if "closed" in full_text:
                status = "Closed"
            elif "open" in full_text or "active" in full_text:
                status = "Open"
            else:
                status = "Unknown"

            return CourtCase(
                case_number=case_number,
                case_type=case_type_default,
                filing_date=filing_date,
                status=status,
                county="Miami-Dade",
                parties="See case details",
            )
        except Exception:
            return None
