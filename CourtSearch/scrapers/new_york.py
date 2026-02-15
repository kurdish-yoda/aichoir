"""
New York State court record scraper.

Searches the NYSCEF (New York State Courts Electronic Filing) system
for civil/financial cases statewide.
Website: https://iapps.courts.state.ny.us/nyscef/
"""

import asyncio
import random
import re
from typing import Optional

from bs4 import BeautifulSoup

from .base import (
    CountyScraper,
    SearchCriteria,
    CourtCase,
)

# Async Playwright for NY scraper (stealth mode)
try:
    from playwright.async_api import async_playwright
    ASYNC_PLAYWRIGHT_AVAILABLE = True
except ImportError:
    ASYNC_PLAYWRIGHT_AVAILABLE = False

# Playwright stealth to bypass bot detection (Cloudflare Turnstile)
try:
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False


class NewYorkScraper(CountyScraper):
    """
    Scraper for New York State Unified Court System.

    Focuses on civil/financial cases statewide for lending due diligence:
    - Civil litigation (contracts, business disputes, debt collection)
    - Commercial cases
    - Insurance disputes
    - Corporate litigation

    Excludes: Criminal, Family, Traffic cases (not relevant for lending)

    Website: https://iapps.courts.state.ny.us/nyscef/
    Search Portal: https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name
    """

    # Base URL for New York courts
    BASE_URL = "https://iapps.courts.state.ny.us"
    SEARCH_URL = f"{BASE_URL}/nyscef/CaseSearch?TAB=name"

    # Stealth mode: randomized viewports to avoid fingerprinting
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
    ]

    # Stealth mode: randomized user agents
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    ]

    # Retry configuration for Cloudflare bypass
    MAX_RETRIES = 3
    BACKOFF_TIMES = [10, 30, 90]  # seconds between retries

    @property
    def county_name(self) -> str:
        return "New York"

    def search(self, criteria: SearchCriteria) -> list[CourtCase]:
        """
        Search New York statewide civil court records by party name.

        Searches the NYSCEF (New York State Courts Electronic Filing) system
        for civil cases across all New York counties. Results are filtered to:
        - Exclude family/criminal cases
        - Only include cases from last 5 years
        - Focus on lending-relevant civil matters
        - Sort by status (Open first) then date (newest first)

        Args:
            criteria: SearchCriteria with at minimum first_name and last_name

        Returns:
            List of CourtCase objects from New York statewide (filtered & sorted)
        """
        if not ASYNC_PLAYWRIGHT_AVAILABLE:
            print("  Error: Playwright is required for New York searches.")
            print("  Install with: pip install playwright && playwright install chromium")
            return []

        # Search civil records only (no criminal/family - not relevant for lending)
        print("    Searching Civil court records statewide...")
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
        Search civil records via the NYSCEF system statewide.

        Args:
            criteria: Search parameters

        Returns:
            List of CourtCase objects from statewide New York courts
        """
        return self._search_with_playwright(
            url=self.SEARCH_URL,
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
        Sync-to-async bridge for Playwright search.

        Delegates to the async implementation which uses stealth mode
        and human-like behavior to bypass Cloudflare Turnstile protection.

        Args:
            url: URL of the search portal
            criteria: Search parameters
            case_type_default: Default case type if not detected

        Returns:
            List of CourtCase objects
        """
        return asyncio.run(self._async_search_with_playwright(url, criteria, case_type_default))

    async def _async_search_with_playwright(
        self,
        url: str,
        criteria: SearchCriteria,
        case_type_default: str
    ) -> list[CourtCase]:
        """
        Execute search using async Playwright with stealth mode.

        Uses randomized browser fingerprints, human-like delays, and
        playwright-stealth to maximize chances of passing Cloudflare
        Turnstile challenge. Retries up to MAX_RETRIES times with
        exponential backoff.

        Args:
            url: URL of the search portal
            criteria: Search parameters
            case_type_default: Default case type if not detected

        Returns:
            List of CourtCase objects
        """
        for attempt in range(self.MAX_RETRIES):
            attempt_num = attempt + 1
            print(f"      Attempt {attempt_num}/{self.MAX_RETRIES} (stealth mode{'+ stealth plugin' if STEALTH_AVAILABLE else ''})")

            browser = None
            try:
                async with async_playwright() as p:
                    # Randomize browser fingerprint each attempt
                    viewport = random.choice(self.VIEWPORTS)
                    user_agent = random.choice(self.USER_AGENTS)

                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        viewport=viewport,
                        user_agent=user_agent,
                        locale="en-US",
                        timezone_id="America/New_York",
                        bypass_csp=True,
                        ignore_https_errors=True,
                    )
                    page = await context.new_page()

                    # Apply stealth patches if available
                    if STEALTH_AVAILABLE:
                        await Stealth().apply_stealth_async(page)

                    # Random pre-navigation delay (appear human)
                    await asyncio.sleep(random.uniform(2, 5))

                    # Navigate to search page
                    await page.goto(url, timeout=30000)
                    await page.wait_for_load_state("domcontentloaded", timeout=15000)

                    # Post-navigation delay (let page settle, Cloudflare JS runs)
                    await asyncio.sleep(random.uniform(4, 8))

                    # Check for Cloudflare challenge
                    if await self._detect_cloudflare_challenge(page):
                        print(f"      Cloudflare challenge detected, waiting for auto-solve...")
                        # Wait for Turnstile to auto-solve
                        await asyncio.sleep(random.uniform(8, 15))

                        # Re-check after waiting
                        if await self._detect_cloudflare_challenge(page):
                            print(f"      Still blocked by Cloudflare")
                            await browser.close()
                            browser = None

                            if attempt < self.MAX_RETRIES - 1:
                                backoff = self.BACKOFF_TIMES[attempt]
                                print(f"      Backing off {backoff}s before retry...")
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                print(f"      All {self.MAX_RETRIES} attempts blocked by Cloudflare")
                                print(f"      NYSCEF requires manual search at: {url}")
                                print(f"      Search: {criteria.first_name} {criteria.last_name}")
                                return []

                    print(f"      Passed Cloudflare challenge")

                    # Wait for full page load
                    try:
                        await page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        pass
                    await asyncio.sleep(random.uniform(1, 3))

                    # Human-like behavior before interacting with form
                    await self._human_mouse_move(page, viewport)
                    await self._random_scroll(page)
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                    # Fill the search form with human-like typing
                    filled_form = await self._async_fill_ny_search_form(page, criteria)

                    if not filled_form:
                        print(f"      Could not find search form fields")
                        return []

                    # Submit the search
                    await self._async_submit_ny_search(page)

                    # Wait for results to load
                    await asyncio.sleep(random.uniform(3, 5))
                    try:
                        await page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        pass

                    # Parse results from rendered page
                    content = await page.content()
                    cases = self._parse_ny_results(content, case_type_default)

                    await browser.close()
                    return cases

            except Exception as e:
                error_msg = str(e)
                if browser:
                    try:
                        await browser.close()
                    except Exception:
                        pass

                if "timeout" in error_msg.lower():
                    print(f"      NYSCEF site unreachable (timeout)")
                else:
                    print(f"      Search error: {e}")

                if attempt < self.MAX_RETRIES - 1:
                    backoff = self.BACKOFF_TIMES[attempt]
                    print(f"      Backing off {backoff}s before retry...")
                    await asyncio.sleep(backoff)
                else:
                    print(f"      For manual search, visit: {url}")
                    print(f"      Search: {criteria.first_name} {criteria.last_name}")

        return []

    async def _detect_cloudflare_challenge(self, page) -> bool:
        """
        Check if the current page is a Cloudflare challenge/interstitial.

        Looks for common Cloudflare indicators:
        - Page title "Just a moment"
        - Turnstile iframe or widget divs
        - "Checking your browser" body text

        Args:
            page: Async Playwright page object

        Returns:
            True if Cloudflare challenge is detected
        """
        try:
            title = (await page.title()).lower()
            if "just a moment" in title:
                return True

            # Check for Turnstile iframe
            turnstile_iframe = page.locator("iframe[src*='challenges.cloudflare.com']")
            if await turnstile_iframe.count() > 0:
                return True

            # Check for Turnstile widget div
            turnstile_div = page.locator("div.cf-turnstile, div[id*='turnstile']")
            if await turnstile_div.count() > 0:
                return True

            # Check body text for challenge indicators
            body_text = await page.locator("body").inner_text()
            body_lower = body_text.lower()
            if "checking your browser" in body_lower or "verify you are human" in body_lower:
                return True

        except Exception:
            pass

        return False

    async def _human_mouse_move(self, page, viewport: dict) -> None:
        """
        Move the mouse through random points to simulate human behavior.

        Args:
            page: Async Playwright page object
            viewport: Viewport dimensions dict with 'width' and 'height'
        """
        try:
            num_points = random.randint(3, 5)
            for _ in range(num_points):
                x = random.randint(100, viewport["width"] - 100)
                y = random.randint(100, viewport["height"] - 100)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.4))
        except Exception:
            pass

    async def _random_scroll(self, page) -> None:
        """
        Perform random scrolling to simulate human browsing.

        Args:
            page: Async Playwright page object
        """
        try:
            scroll_amount = random.randint(50, 300)
            await page.mouse.wheel(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Occasionally scroll back up
            if random.random() < 0.3:
                await page.mouse.wheel(0, -random.randint(20, 100))
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass

    async def _human_type(self, page, selector: str, text: str) -> None:
        """
        Type text with random per-character delay to simulate human typing.

        Args:
            page: Async Playwright page object
            selector: CSS selector for the input field
            text: Text to type
        """
        await page.type(selector, text, delay=random.uniform(80, 150))

    async def _async_fill_ny_search_form(self, page, criteria: SearchCriteria) -> bool:
        """
        Fill in the NYSCEF search form with human-like typing behavior.

        Args:
            page: Async Playwright page object
            criteria: Search criteria to fill in

        Returns:
            True if form was successfully filled, False otherwise
        """
        filled_first = False
        filled_last = False

        # NYSCEF form selectors - try various patterns
        first_name_selectors = [
            "input[name*='firstName']",
            "input[name*='FirstName']",
            "input[id*='firstName']",
            "input[id*='FirstName']",
            "input[placeholder*='first']",
            "input[placeholder*='First']",
            "#firstName",
            "#txtFirstName",
            "input[name='firstName']",
        ]

        last_name_selectors = [
            "input[name*='lastName']",
            "input[name*='LastName']",
            "input[id*='lastName']",
            "input[id*='LastName']",
            "input[placeholder*='last']",
            "input[placeholder*='Last']",
            "#lastName",
            "#txtLastName",
            "input[name='lastName']",
        ]

        # Fill first name
        for selector in first_name_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0 and await locator.first.is_visible():
                    await locator.first.click()
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    await self._human_type(page, selector, criteria.first_name)
                    filled_first = True
                    break
            except Exception:
                continue

        await asyncio.sleep(random.uniform(0.5, 1.2))

        # Fill last name
        for selector in last_name_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0 and await locator.first.is_visible():
                    await locator.first.click()
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    await self._human_type(page, selector, criteria.last_name)
                    filled_last = True
                    break
            except Exception:
                continue

        # Optionally fill middle name if available
        if criteria.middle_name:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            middle_selectors = [
                "input[name*='middleName']",
                "input[name*='MiddleName']",
                "input[id*='middleName']",
                "input[id*='MiddleName']",
                "input[placeholder*='middle']",
                "input[placeholder*='Middle']",
                "#middleName",
                "#txtMiddleName",
                "input[name='middleName']",
            ]
            for selector in middle_selectors:
                try:
                    locator = page.locator(selector)
                    if await locator.count() > 0 and await locator.first.is_visible():
                        await locator.first.click()
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        await self._human_type(page, selector, criteria.middle_name)
                        break
                except Exception:
                    continue

        # Optionally fill date of birth if available
        if criteria.date_of_birth:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            dob_selectors = [
                "input[name*='DOB']",
                "input[name*='dateOfBirth']",
                "input[id*='DOB']",
                "input[id*='dateOfBirth']",
                "input[placeholder*='DOB']",
                "input[placeholder*='birth']",
                "input[placeholder*='Birth']",
                "#DOB",
                "#txtDOB",
                "input[name='DOB']",
            ]
            for selector in dob_selectors:
                try:
                    locator = page.locator(selector)
                    if await locator.count() > 0 and await locator.first.is_visible():
                        await locator.first.click()
                        await asyncio.sleep(random.uniform(0.3, 0.8))
                        await self._human_type(page, selector, criteria.date_of_birth)
                        print(f"        Using DOB filter: {criteria.date_of_birth}")
                        break
                except Exception:
                    continue

        # Try to set statewide search if available
        statewide_selectors = [
            "select[name*='county'] option[value*='all']",
            "select[name*='county'] option:contains('All')",
            "select[name*='county'] option:contains('Statewide')",
            "select[id*='county'] option[value*='all']",
            "select[id*='county'] option:contains('All')",
            "input[name*='statewide']",
            "input[id*='statewide']",
        ]

        for selector in statewide_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    await locator.first.click()
                    print("        Selected statewide search")
                    break
            except Exception:
                continue

        return filled_first and filled_last

    async def _async_submit_ny_search(self, page) -> None:
        """
        Submit the search form with human-like behavior.

        Args:
            page: Async Playwright page object
        """
        submit_selectors = [
            "button:has-text('Search')",
            "input[type='submit']",
            "button[type='submit']",
            "input[value='Search']",
            "input[value='Submit']",
            "#btnSearch",
            ".search-button",
            "button.search",
        ]

        for selector in submit_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    # Occasionally hover before clicking (human behavior)
                    if random.random() < 0.4:
                        await locator.first.hover()
                        await asyncio.sleep(random.uniform(0.2, 0.6))
                    await locator.first.click()
                    return
            except Exception:
                continue

        # Fallback: try pressing Enter
        try:
            await page.keyboard.press("Enter")
        except Exception:
            pass

    def _parse_ny_results(self, html_content: str, case_type_default: str) -> list[CourtCase]:
        """
        Parse search results from New York NYSCEF system.

        NYSCEF results are typically displayed in tables or structured lists.
        Look for case information in various formats.

        Args:
            html_content: Full HTML content of the rendered page
            case_type_default: Default case type

        Returns:
            List of CourtCase objects extracted from the page
        """
        cases = []
        soup = BeautifulSoup(html_content, "lxml")

        # Try to find results table
        results_table = soup.find("table", {"id": re.compile(r"(?i)result|case|search")})
        if results_table:
            cases = self._parse_ny_table(results_table, case_type_default)
        else:
            # Look for other result containers
            result_containers = soup.find_all("div", class_=re.compile(r"(?i)result|case|item"))
            for container in result_containers:
                case = self._parse_ny_container(container, case_type_default)
                if case:
                    cases.append(case)

            # If no structured results, try generic table parsing
            if not cases:
                for table in soup.find_all("table"):
                    table_cases = self._parse_ny_table(table, case_type_default)
                    cases.extend(table_cases)

        return cases

    def _parse_ny_table(self, table, case_type_default: str) -> list[CourtCase]:
        """
        Parse NYSCEF results from a table structure.

        Args:
            table: BeautifulSoup table element
            case_type_default: Default case type

        Returns:
            List of CourtCase objects
        """
        cases = []

        rows = table.find_all("tr")[1:]  # Skip header
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:
                case = self._parse_ny_table_row(cells, case_type_default)
                if case:
                    cases.append(case)

        return cases

    def _parse_ny_table_row(self, cells: list, case_type_default: str) -> Optional[CourtCase]:
        """
        Parse a NYSCEF table row into a CourtCase object.

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

            # Try to identify columns - NYSCEF may have different column order
            case_number = ""
            filing_date = ""
            status = ""
            parties = ""
            case_type = case_type_default

            for i, text in enumerate(cell_texts):
                # Look for case number patterns (NYSCEF often uses specific formats)
                if re.search(r'\d{4,}', text) and ('-' in text or '/' in text):
                    case_number = text
                # Look for date patterns
                elif re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text):
                    filing_date = text
                # Look for status keywords
                elif any(word in text.upper() for word in ['OPEN', 'CLOSED', 'ACTIVE', 'PENDING', 'DISPOSED', 'DECIDED']):
                    status = text.title()

            # Fallback positional parsing if pattern matching fails
            if not case_number and len(cell_texts) >= 1:
                case_number = cell_texts[0]
            if not filing_date and len(cell_texts) >= 2:
                filing_date = cell_texts[1]
            if not status and len(cell_texts) >= 3:
                status = cell_texts[2]
            if not parties and len(cell_texts) >= 4:
                parties = cell_texts[3]

            if not case_number:
                return None

            # Classify case type from available information
            case_type = self._classify_ny_case_type(case_type, parties, cell_texts)

            # Generate verification instructions
            verification_instructions = (
                f"To verify this case manually: "
                f"1. Visit https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name "
                f"2. Search for Case Number: {case_number} "
                f"3. Verify all details match your records"
            )

            return CourtCase(
                case_number=case_number,
                case_type=case_type,
                filing_date=filing_date,
                status=status,
                county="New York",
                parties=parties,
                verification_instructions=verification_instructions,
                search_results_url="https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name",
            )
        except Exception:
            return None

    def _parse_ny_container(self, container, case_type_default: str) -> Optional[CourtCase]:
        """
        Parse a NYSCEF result container (fallback parsing).

        Args:
            container: BeautifulSoup element containing case data
            case_type_default: Default case type

        Returns:
            CourtCase object or None
        """
        try:
            text = container.get_text()

            # Extract case number
            case_number_match = re.search(r'\d{4,}[\-/]\d+', text)
            case_number = case_number_match.group() if case_number_match else ""

            if not case_number:
                return None

            # Extract date
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            filing_date = date_match.group() if date_match else "N/A"

            # Extract status
            if "closed" in text.lower() or "disposed" in text.lower() or "decided" in text.lower():
                status = "Closed"
            elif "open" in text.lower() or "active" in text.lower() or "pending" in text.lower():
                status = "Open"
            else:
                status = "Unknown"

            # Classify case type
            case_type = self._classify_ny_case_type(case_type_default, text, [])

            # Generate verification instructions
            verification_instructions = (
                f"To verify this case manually: "
                f"1. Visit https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name "
                f"2. Search for Case Number: {case_number} "
                f"3. Verify all details match your records"
            )

            return CourtCase(
                case_number=case_number,
                case_type=case_type,
                filing_date=filing_date,
                status=status,
                county="New York",
                parties="See case details",
                verification_instructions=verification_instructions,
                search_results_url="https://iapps.courts.state.ny.us/nyscef/CaseSearch?TAB=name",
            )
        except Exception:
            return None

    def _classify_ny_case_type(self, current_type: str, parties: str, cell_texts: list) -> str:
        """
        Classify New York case type from available information.

        New York uses different classification than Florida:
        - Commercial cases
        - Contract disputes
        - Business litigation
        - Insurance matters

        Args:
            current_type: Current case type detected
            parties: Party information text
            cell_texts: Additional cell text data

        Returns:
            Classified case type string
        """
        # Combine all available text for analysis
        all_text = f"{current_type} {parties} {' '.join(cell_texts)}".upper()

        # Commercial/Business litigation
        if any(term in all_text for term in ['COMMERCIAL', 'BUSINESS', 'CORPORATE', 'COMPANY', 'LLC', 'INC']):
            return "Commercial"

        # Contract disputes
        elif any(term in all_text for term in ['CONTRACT', 'BREACH', 'AGREEMENT']):
            return "Contract"

        # Insurance matters
        elif any(term in all_text for term in ['INSURANCE', 'INSURER', 'CLAIM']):
            return "Insurance"

        # Debt collection
        elif any(term in all_text for term in ['DEBT', 'COLLECTION', 'CREDITOR']):
            return "Debt Collection"

        # Real estate
        elif any(term in all_text for term in ['REAL ESTATE', 'PROPERTY', 'FORECLOSURE']):
            return "Real Estate"

        # Professional malpractice
        elif any(term in all_text for term in ['MALPRACTICE', 'PROFESSIONAL']):
            return "Professional Malpractice"

        # Default to Civil if not classified
        elif current_type == "Civil" or any(term in all_text for term in ['CIVIL', 'LAWSUIT', 'ACTION']):
            return "Civil"

        return current_type
