"""
Broward County court record scraper.

Searches the Broward County Clerk subscriber portal for civil/financial cases.
Website: https://www.browardclerk.org/Web2/
"""

import time
from datetime import datetime, timedelta
from typing import Optional

from bs4 import BeautifulSoup

from .base import (
    CountyScraper,
    SearchCriteria,
    CourtCase,
    CASE_AGE_LIMIT_YEARS,
    PLAYWRIGHT_AVAILABLE,
)

if PLAYWRIGHT_AVAILABLE:
    from playwright.sync_api import sync_playwright


class BrowardScraper(CountyScraper):
    """
    Scraper for Broward County Clerk court records.

    Focused on civil/financial cases for lending due diligence:
    - Civil lawsuits, foreclosures, judgments
    - Small claims
    - Probate (creditor claims only)

    Excludes: Criminal cases, Family court (not relevant for lending)

    Uses subscriber-level access (registered account) to avoid CAPTCHA blocks.

    Website: https://www.browardclerk.org/Web2/
    Search Portal: https://www.browardclerk.org/Web2/CaseSearchECA/Index/?AccessLevel=SUBSCRIBER
    """

    # Base URL for Broward Clerk court records
    BASE_URL = "https://www.browardclerk.org"
    LOGIN_URL = f"{BASE_URL}/Web2/Account/Login/"
    SEARCH_URL = f"{BASE_URL}/Web2/CaseSearchECA/Index/?AccessLevel=SUBSCRIBER"

    # Subscriber credentials
    BROWARD_USERNAME = "kurdishYoda"
    BROWARD_PASSWORD = "Courtsearch1!"

    @property
    def county_name(self) -> str:
        return "Broward"

    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search Broward civil court records by party name.

        Searches the OCS portal for civil, probate, and small claims cases.
        Results are filtered to:
        - Exclude family/criminal cases
        - Only include cases from last 5 years
        - Sort by status (Open first) then date (newest first)

        Args:
            criteria: SearchCriteria with at minimum first_name and last_name

        Returns:
            List of CourtCase objects from Broward County (filtered & sorted)
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("  Error: Playwright is required for Broward searches.")
            print("  Install with: pip install playwright && playwright install chromium")
            return []

        # Search civil records only (no criminal - not relevant for lending)
        print("    Searching Civil court records...")
        cases = self._search_civil_records(criteria)

        # Filter and sort results for lending relevance
        filtered_cases = self._filter_and_sort_cases(cases, criteria)

        print(f"      Found {len(filtered_cases)} relevant case(s) (after filtering)")

        # Warn if too many results (likely too broad search)
        if len(filtered_cases) > 20:
            print(f"      Warning: {len(filtered_cases)} cases found. This may indicate a very common name.")
            print(f"      Consider providing middle name or DOB for more specific results.")

        return filtered_cases

    def _search_civil_records(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search civil records via the Broward OCS portal.

        Args:
            criteria: Search parameters

        Returns:
            List of CourtCase objects from civil courts
        """
        return self._search_with_playwright(
            url=self.SEARCH_URL,
            criteria=criteria,
            case_type_default="Civil"
        )

    def _login_to_broward(self, page) -> bool:
        """
        Log in to Broward County Clerk subscriber portal.

        Navigates to the login page, fills credentials, accepts terms,
        and submits the login form.

        Args:
            page: Playwright page object

        Returns:
            True if login was successful, False otherwise
        """
        try:
            print("      Logging in to Broward County subscriber portal...")
            page.goto(self.LOGIN_URL, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(2)

            # Fill username
            username_selectors = [
                "input[name='Username']",
                "input[name='username']",
                "input[id*='Username']",
                "input[id*='username']",
                "input[type='text']",
            ]
            filled_user = False
            for selector in username_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.fill(self.BROWARD_USERNAME)
                        filled_user = True
                        break
                except Exception:
                    continue

            # Fill password
            password_selectors = [
                "input[name='Password']",
                "input[name='password']",
                "input[type='password']",
            ]
            filled_pass = False
            for selector in password_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.fill(self.BROWARD_PASSWORD)
                        filled_pass = True
                        break
                except Exception:
                    continue

            if not (filled_user and filled_pass):
                print("      Could not find login form fields")
                return False

            # Accept terms checkbox
            terms_selectors = [
                "input[name='terms']",
                "input[id*='terms']",
                "input[type='checkbox']",
            ]
            for selector in terms_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0:
                        if not loc.first.is_checked():
                            loc.first.check()
                        break
                except Exception:
                    continue

            # Submit login form - find visible login button
            submitted = False
            login_buttons = page.locator("button").all()
            for btn in login_buttons:
                try:
                    if btn.is_visible() and "log" in (btn.text_content() or "").lower():
                        btn.click()
                        submitted = True
                        break
                except Exception:
                    continue

            if not submitted:
                # Fallback: submit the form directly via JavaScript
                try:
                    page.locator("#loginForm").evaluate("form => form.submit()")
                except Exception:
                    page.keyboard.press("Enter")

            # Wait for login to complete
            page.wait_for_load_state("networkidle", timeout=30000)
            time.sleep(3)

            # Verify login succeeded by checking URL or page content
            current_url = page.url.lower()
            if "login" in current_url:
                # Still on login page - check for error messages
                content = page.content().lower()
                if "invalid" in content or "incorrect" in content or "error" in content:
                    print("      Login failed: Invalid credentials")
                    return False
                # Might still be on login page due to redirect delay
                time.sleep(2)

            print("      Login successful")
            return True

        except Exception as e:
            print(f"      Login error: {e}")
            return False

    def _search_with_playwright(
        self,
        url: str,
        criteria: SearchCriteria,
        case_type_default: str
    ) -> list[CourtCase]:
        """
        Execute search using Playwright with subscriber-level access.

        This method:
        1. Logs in to the Broward Clerk subscriber portal
        2. Navigates to the subscriber case search page
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
                # Step 1: Log in to the subscriber portal
                logged_in = self._login_to_broward(page)
                if not logged_in:
                    print("      Could not log in to Broward subscriber portal")
                    print(f"      For manual search, visit: {self.SEARCH_URL}")
                    print(f"      Search: {criteria.first_name} {criteria.last_name}")
                    return []

                # Step 2: Navigate to subscriber case search
                page.goto(self.SEARCH_URL, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(3)

                # Select the Party Name search tab
                party_selectors = [
                    "a:has-text('Party Name')",
                    "button:has-text('Party Name')",
                    ".tab:has-text('Party Name')",
                    "[role='tab']:has-text('Party Name')",
                    "#partyNameTab",
                    "[href*='Party']",
                    "li:has-text('Party Name')",
                    "a:has-text('Party')",
                ]

                for selector in party_selectors:
                    try:
                        loc = page.locator(selector)
                        if loc.count() > 0 and loc.first.is_visible():
                            loc.first.click()
                            page.wait_for_load_state("networkidle", timeout=30000)
                            time.sleep(2)
                            break
                    except Exception:
                        continue

                # Step 3: Fill the search form
                filled_form = self._fill_broward_search_form(page, criteria)

                if not filled_form:
                    print(f"      Standard form fill failed, trying emergency detection...")
                    filled_form = self._emergency_broward_form_fill(page, criteria)

                if not filled_form:
                    print(f"      Could not fill search form")
                    print(f"      For manual search, visit: {self.SEARCH_URL}")
                    return []

                # Step 4: Submit the search
                self._submit_broward_search(page)

                # Wait for results page to navigate and fully render
                # The results page uses a Kendo UI grid that loads data via AJAX
                time.sleep(3)
                page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(3)

                # Wait for the Kendo grid pagination to appear (signals data is loaded)
                try:
                    page.wait_for_selector(".k-pager-numbers", timeout=20000)
                    time.sleep(2)
                except Exception:
                    # Fallback: just wait longer for AJAX
                    time.sleep(5)

                # Extract data directly from the Kendo grid via JavaScript
                # The Kendo grid stores data in memory; DOM may not have it yet
                try:
                    grid_data = page.evaluate("""() => {
                        const grid = $(".k-grid").data("kendoGrid");
                        if (!grid) return null;
                        const data = grid.dataSource.data();
                        return data.map(item => item.toJSON ? item.toJSON() : item);
                    }""")
                    if grid_data:
                        cases = self._parse_kendo_data(grid_data, case_type_default)
                except Exception:
                    pass
                    # Fallback: parse the rendered HTML
                    content = page.content()
                    cases = self._parse_broward_results(content, case_type_default)

            except Exception as e:
                print(f"      Search error: {e}")
            finally:
                browser.close()

        return cases

    def _parse_kendo_data(self, grid_data: list, case_type_default: str) -> list[CourtCase]:
        """
        Parse case data extracted directly from the Kendo grid's JavaScript data source.

        Kendo grid fields:
            CaseNumber, Style, CourtType, CaseFiledDate (ISO), SortCaseFiledDate,
            DispositionCode, CaseStatusDesc, JudgeName, CourtLocation,
            CaseUTypeDesc, CaseCategoryKey

        Args:
            grid_data: List of dicts from the Kendo grid dataSource
            case_type_default: Default case type

        Returns:
            List of CourtCase objects
        """
        cases = []
        for item in grid_data:
            try:
                case_number = str(item.get("CaseNumber", ""))
                if not case_number:
                    continue

                parties = str(item.get("Style", "")).strip()
                court_type = str(item.get("CourtType", ""))
                case_subtype = str(item.get("CaseUTypeDesc", ""))
                case_type_raw = f"{court_type} {case_subtype}".strip()

                # Parse filing date from ISO format (e.g. "1984-04-01 22:00:00+00:00")
                # or SortCaseFiledDate (e.g. "1984/04/02")
                sort_date = str(item.get("SortCaseFiledDate", ""))
                if sort_date:
                    # Convert YYYY/MM/DD to MM/DD/YYYY
                    parts = sort_date.split("/")
                    if len(parts) == 3:
                        filing_date = f"{parts[1]}/{parts[2]}/{parts[0]}"
                    else:
                        filing_date = sort_date
                else:
                    filing_date = "N/A"

                # Status from DispositionCode or CaseStatusDesc
                disposition = str(item.get("DispositionCode", ""))
                status_desc = str(item.get("CaseStatusDesc", ""))
                status_raw = disposition or status_desc

                # Classify case type
                case_type = self._classify_broward_case_type(case_type_raw, case_type_default)

                # Normalize status
                status_upper = status_raw.upper()
                if "CLOSED" in status_upper or "DISPOSED" in status_upper:
                    status = "Closed"
                elif "OPEN" in status_upper or "ACTIVE" in status_upper or "PENDING" in status_upper:
                    status = "Open"
                else:
                    status = status_raw.title() if status_raw else "Unknown"

                # Extract additional details
                judge = str(item.get("JudgeName", ""))
                court_division = str(item.get("CourtLocation", ""))
                disposition_date = str(item.get("CaseStatusDate", ""))

                verification_instructions = (
                    f"To verify this case manually: "
                    f"1. Visit {self.SEARCH_URL} "
                    f"2. Search for Case Number: {case_number} "
                    f"3. Verify all details match your records"
                )

                cases.append(CourtCase(
                    case_number=case_number,
                    case_type=case_type,
                    filing_date=filing_date,
                    status=status,
                    county="Broward",
                    parties=parties,
                    court_division=court_division,
                    judge=judge,
                    disposition_date=disposition_date,
                    verification_instructions=verification_instructions,
                    search_results_url=self.SEARCH_URL,
                ))
            except Exception:
                continue

        return cases

    def _fill_broward_search_form(self, page, criteria: SearchCriteria) -> bool:
        """
        Fill in the search form fields for Broward County subscriber case search.

        Uses known field IDs from the subscriber portal form.

        Args:
            page: Playwright page object
            criteria: Search criteria to fill in

        Returns:
            True if form was successfully filled, False otherwise
        """
        filled_last = False
        filled_first = False

        # Broward subscriber portal uses these specific field IDs
        # lastName is type='search', firstName/middleName are type='text'
        last_name_selectors = [
            "#lastName",
            "input[name='lastName']",
            "input[placeholder='Last Name']",
        ]

        first_name_selectors = [
            "#firstName",
            "input[name='firstName']",
            "input[placeholder='First Name']",
        ]

        # Fill last name
        for selector in last_name_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.fill(criteria.last_name)
                    filled_last = True
                    break
            except Exception:
                continue

        # Fill first name
        for selector in first_name_selectors:
            try:
                loc = page.locator(selector)
                if loc.count() > 0 and loc.first.is_visible():
                    loc.first.fill(criteria.first_name)
                    filled_first = True
                    break
            except Exception:
                continue

        # Optionally fill middle name
        if criteria.middle_name:
            middle_selectors = [
                "#middleName",
                "input[name='middleName']",
                "input[placeholder='Middle Name']",
            ]
            for selector in middle_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.fill(criteria.middle_name)
                        break
                except Exception:
                    continue

        # Optionally fill filing date range to limit to last N years
        try:
            from_date = (datetime.now() - timedelta(days=CASE_AGE_LIMIT_YEARS * 365)).strftime("%m/%d/%Y")
            date_from_selectors = [
                "#filingDateOnOrAfterP",
                "input[name='filingDateOnOrAfterP']",
            ]
            for selector in date_from_selectors:
                try:
                    loc = page.locator(selector)
                    if loc.count() > 0 and loc.first.is_visible():
                        loc.first.fill(from_date)
                        loc.first.dispatch_event("change")
                        break
                except Exception:
                    continue
        except Exception:
            pass

        return filled_first and filled_last

    def _emergency_broward_form_fill(self, page, criteria: SearchCriteria) -> bool:
        """
        Emergency fallback for Broward form filling.
        Try to find ANY text input and use the first two for names.

        Args:
            page: Playwright page object
            criteria: Search criteria

        Returns:
            True if form was filled, False otherwise
        """
        try:
            # Try to find any input that might accept text
            all_inputs = page.locator("input").all()
            text_inputs = []

            for inp in all_inputs:
                try:
                    input_type = inp.get_attribute("type") or "text"
                    if input_type in ["text", "search", "email", "", None]:
                        if inp.is_visible():
                            text_inputs.append(inp)
                except:
                    continue

            print(f"      Emergency mode: Found {len(text_inputs)} visible text inputs")

            if len(text_inputs) >= 2:
                # Try to fill the first two visible text inputs
                try:
                    text_inputs[0].fill(criteria.first_name)
                    text_inputs[1].fill(criteria.last_name)
                    print(f"      Emergency fill successful: {criteria.first_name} {criteria.last_name}")
                    return True
                except Exception as e:
                    print(f"      Emergency fill failed: {e}")

            # If that doesn't work, try clicking on the page to activate dynamic content
            try:
                print("      Trying to click page to activate dynamic content...")
                page.click("body", timeout=5000)
                time.sleep(2)

                # Check again for inputs after clicking
                all_inputs = page.locator("input").all()
                text_inputs = []
                for inp in all_inputs:
                    try:
                        input_type = inp.get_attribute("type") or "text"
                        if input_type in ["text", "search", "email", "", None]:
                            if inp.is_visible():
                                text_inputs.append(inp)
                    except:
                        continue

                print(f"      After click: Found {len(text_inputs)} visible text inputs")

                if len(text_inputs) >= 2:
                    text_inputs[0].fill(criteria.first_name)
                    text_inputs[1].fill(criteria.last_name)
                    print(f"      Emergency fill after click successful: {criteria.first_name} {criteria.last_name}")
                    return True

            except Exception as e:
                print(f"      Click activation failed: {e}")

        except Exception as e:
            print(f"      Emergency form detection completely failed: {e}")

        return False

    def _has_captcha(self, page) -> bool:
        """
        Check if the Broward County page contains a CAPTCHA challenge.

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
            "iframe[src*='hcaptcha']",
            ".hcaptcha",
            "#hcaptcha",
        ]

        for selector in captcha_indicators:
            try:
                if page.locator(selector).count() > 0:
                    print(f"      Found CAPTCHA indicator: {selector}")
                    return True
            except Exception:
                continue

        # Check page content for CAPTCHA-specific text
        try:
            content = page.content().lower()
            captcha_keywords = ['captcha', 'recaptcha', 'hcaptcha', "i'm not a robot"]
            for keyword in captcha_keywords:
                if keyword in content:
                    print(f"      Found CAPTCHA keyword in page content: '{keyword}'")
                    return True
        except Exception:
            pass

        return False

    def _submit_broward_search(self, page):
        """
        Submit the search form by clicking the PersonSearchResults button.

        Args:
            page: Playwright page object
        """
        # The subscriber portal has a specific button for party name search
        submit_selectors = [
            "#PersonSearchResults",
            "button:has-text('Search'):visible",
            "button[type='submit']:visible",
        ]

        for selector in submit_selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible():
                    locator.first.click()
                    return
            except Exception:
                continue

        # Fallback: try pressing Enter
        try:
            page.keyboard.press("Enter")
        except Exception:
            pass

    def _parse_broward_results(self, html_content: str, case_type_default: str) -> list[CourtCase]:
        """
        Parse search results from Broward County subscriber portal.

        The results page uses a Kendo UI grid with tables. The data table
        has columns: Case Number, Case Style, Case Type, Filing Date,
        Case Status, Access Level.

        Args:
            html_content: Full HTML content of the rendered page
            case_type_default: Default case type

        Returns:
            List of CourtCase objects extracted from the page
        """
        cases = []
        soup = BeautifulSoup(html_content, "lxml")

        # Find all tables and look for the one with case data rows
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue

            for row in rows:
                cells = row.find_all("td")
                # The data table has 6 columns:
                # Case Number, Case Style, Case Type, Filing Date, Case Status, Access Level
                if len(cells) >= 5:
                    case = self._parse_broward_table_row(cells, case_type_default)
                    if case:
                        cases.append(case)

        return cases

    def _parse_broward_table_row(self, cells: list, case_type_default: str) -> Optional[CourtCase]:
        """
        Parse a Broward subscriber portal table row into a CourtCase object.

        Known column order: Case Number, Case Style, Case Type, Filing Date,
        Case Status, Access Level.

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

            # Positional parsing based on known column order
            case_number = cell_texts[0] if len(cell_texts) > 0 else ""
            parties = cell_texts[1] if len(cell_texts) > 1 else ""
            case_type_raw = cell_texts[2] if len(cell_texts) > 2 else case_type_default
            filing_date = cell_texts[3] if len(cell_texts) > 3 else "N/A"
            status_raw = cell_texts[4] if len(cell_texts) > 4 else "Unknown"

            if not case_number:
                return None

            # Classify case type
            case_type = self._classify_broward_case_type(case_type_raw, case_type_default)

            # Normalize status
            status_upper = status_raw.upper()
            if "CLOSED" in status_upper or "DISPOSED" in status_upper:
                status = "Closed"
            elif "OPEN" in status_upper or "ACTIVE" in status_upper or "PENDING" in status_upper:
                status = "Open"
            else:
                status = status_raw.title() if status_raw else "Unknown"

            # Normalize filing date (Broward uses MM-DD-YYYY format)
            filing_date = filing_date.replace("-", "/")

            # Generate verification instructions
            verification_instructions = (
                f"To verify this case manually: "
                f"1. Visit {self.SEARCH_URL} "
                f"2. Search for Case Number: {case_number} "
                f"3. Verify all details match your records"
            )

            return CourtCase(
                case_number=case_number,
                case_type=case_type,
                filing_date=filing_date,
                status=status,
                county="Broward",
                parties=parties,
                verification_instructions=verification_instructions,
                search_results_url=self.SEARCH_URL,
            )
        except Exception:
            return None

    def _classify_broward_case_type(self, case_type_raw: str, default: str) -> str:
        """
        Classify Broward case type from the raw case type text.

        Args:
            case_type_raw: Raw case type text from the table
            default: Default case type

        Returns:
            Classified case type string
        """
        ct = case_type_raw.upper()

        if any(term in ct for term in ["FELONY", "CRIMINAL"]):
            return "Criminal Felony"
        elif any(term in ct for term in ["MISDEMEANOR"]):
            return "Criminal Misdemeanor"
        elif any(term in ct for term in ["FAMILY", "DIVORCE", "CUSTODY", "DISSOLUTION"]):
            return "Family"
        elif any(term in ct for term in ["TRAFFIC", "INFRACTION"]):
            return "Traffic"
        elif any(term in ct for term in ["FORECLOSURE"]):
            return "Foreclosure"
        elif any(term in ct for term in ["SMALL CLAIMS"]):
            return "Small Claims"
        elif any(term in ct for term in ["PROBATE", "ESTATE", "ADMINISTRATION", "WILL"]):
            return "Probate"
        elif any(term in ct for term in ["CIVIL", "CONTRACT", "NEGLIGENCE", "TORT"]):
            return "Civil"
        elif any(term in ct for term in ["PETITION", "CLAIM"]):
            return "Civil"
        else:
            return default
