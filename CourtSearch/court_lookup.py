#!/usr/bin/env python3
"""
Court Records Lookup CLI - Lending Due Diligence Edition

Thin CLI entrypoint that imports all scraping logic from the scrapers/ package.

Usage:
    python court_lookup.py

Dependencies:
    - requests
    - beautifulsoup4
    - playwright
    - tabulate
    - python-dateutil
"""

import re
import sys
from datetime import datetime

from scrapers import (
    SearchCriteria,
    CourtCase,
    search_court_records,
    get_api_response,
    CASE_AGE_LIMIT_YEARS,
)


def get_user_input() -> SearchCriteria:
    """
    Prompt user for search criteria via interactive console input.

    Returns:
        SearchCriteria object populated with user's input

    Raises:
        SystemExit: If required fields are not provided
    """
    print("\n" + "=" * 60)
    print("FLORIDA COURT RECORDS - LENDING DUE DILIGENCE")
    print("=" * 60)
    print("(Searches civil/financial cases only - last 5 years)")
    print("(Automatically searches all available counties)")
    print()

    # Get required fields
    first_name = input("Enter First Name: ").strip()
    if not first_name:
        print("Error: First name is required.")
        sys.exit(1)

    last_name = input("Enter Last Name: ").strip()
    if not last_name:
        print("Error: Last name is required.")
        sys.exit(1)

    # Get optional fields
    middle_name = input("Enter Middle Name (or press Enter to skip): ").strip() or None

    dob = input("Enter Date of Birth MM/DD/YYYY (or press Enter to skip): ").strip()
    if dob:
        # Validate date format and actual date validity
        if not re.match(r"^\d{2}/\d{2}/\d{4}$", dob):
            print("Warning: Date format should be MM/DD/YYYY. Ignoring DOB filter.")
            dob = None
        else:
            # Validate the actual date values
            try:
                month, day, year = map(int, dob.split('/'))
                # Check valid ranges
                if not (1 <= month <= 12):
                    print("Warning: Month must be between 01-12. Ignoring DOB filter.")
                    dob = None
                elif not (1 <= day <= 31):
                    print("Warning: Day must be between 01-31. Ignoring DOB filter.")
                    dob = None
                elif not (1900 <= year <= datetime.now().year):
                    print(f"Warning: Year must be between 1900-{datetime.now().year}. Ignoring DOB filter.")
                    dob = None
                else:
                    # Additional validation for specific month/day combinations
                    import calendar
                    if day > calendar.monthrange(year, month)[1]:
                        print(f"Warning: Invalid day {day} for month {month}. Ignoring DOB filter.")
                        dob = None
            except ValueError:
                print("Warning: Invalid date format. Ignoring DOB filter.")
            dob = None
    else:
        dob = None

    # No longer prompt for county - will search all available counties
    print("Note: Will search all available counties automatically.")

    return SearchCriteria(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        date_of_birth=dob,
        county=None,  # Set to None to trigger statewide search
    )


def display_results(cases: list[CourtCase], criteria: SearchCriteria):
    """
    Display search results in a formatted table.

    Results are pre-sorted with OPEN cases first (current legal exposure),
    then by date (most recent first).

    Args:
        cases: List of CourtCase objects to display
        criteria: Original search criteria (for display purposes)
    """
    print()

    if not cases:
        print("=" * 60)
        print("RESULT: NO RELEVANT CASES FOUND")
        print("=" * 60)
        print()
        print(f"No civil/financial court cases found for: {criteria.first_name} {criteria.last_name}")
        print(f"(Searched: last {CASE_AGE_LIMIT_YEARS} years)")
        print()
        print("Note: This could mean:")
        print("  - No civil court records exist for this person")
        print("  - Records may exist under a different name spelling")
        print("  - The search requires authentication (registration may be needed)")
        return

    # Count open vs closed cases
    open_cases = [c for c in cases if c.status.upper() in ("OPEN", "ACTIVE", "PENDING")]
    closed_cases = [c for c in cases if c not in open_cases]

    print("=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)
    print()
    print(f"Person: {criteria.first_name} {criteria.last_name}")
    print(f"Period: Last {CASE_AGE_LIMIT_YEARS} years")
    print()

    # Summary
    if open_cases:
        print(f"OPEN/ACTIVE CASES: {len(open_cases)}")
    else:
        print(f"No open/active cases")
    print(f"   Closed cases: {len(closed_cases)}")
    print(f"   Total: {len(cases)}")
    print()

    # Display detailed case information for OPEN/ACTIVE cases only
    if open_cases:
        print("OPEN/ACTIVE CASES DETAILS:")
        print("-" * 50)
        for i, case in enumerate(open_cases, 1):
            print(f"\n--- OPEN CASE {i} ---")
            print(f"Case Number: {case.case_number}")
            print(f"Type: {case.case_type}")
            print(f"Filed: {case.filing_date}")
            print(f"Status: {case.status.upper()}")
            print(f"County: {case.county}")
            print(f"Parties: {case.parties}")

            # Display additional comprehensive details
            if case.court_division:
                print(f"Division: {case.court_division}")
            if case.judge:
                print(f"Judge: {case.judge}")
            if case.amount:
                print(f"Amount: {case.amount}")
            if case.disposition_date:
                print(f"Disposition Date: {case.disposition_date}")
            if case.section:
                print(f"Section: {case.section}")

            print(f"\nVerification Instructions: {case.verification_instructions}")
            print(f"View All Results: {case.search_results_url}")
            print("-" * 50)
    else:
        print("No open/active cases to display in detail.")

    print(f"\nSUMMARY: {len(cases)} total case(s) found ({len(open_cases)} open/active, {len(closed_cases)} closed)")
    print()


def print_disclaimer():
    """Print legal disclaimer about search results."""
    print()
    print("-" * 60)
    print("DISCLAIMER - FOR INTERNAL DUE DILIGENCE USE")
    print("-" * 60)
    print("""
This search tool is for preliminary lending due diligence only.
Results must be verified with official court records before
making any lending decisions.

IMPORTANT:
- Data may not be complete or current
- Multiple people may share the same name - verify identity
- Excluded: Criminal cases, Family court (not relevant)
- Only showing cases from the last 5 years
- Open cases indicate current legal exposure

For official verification, visit:
  https://www.myflcourtaccess.com
  https://www.miamidadeclerk.gov
""")
    print("-" * 60)


def main():
    """
    Main entry point for the court lookup script.

    Handles user input, automatically searches all available counties,
    and displays comprehensive results with verification instructions.
    """
    try:
        # Get search criteria from user
        criteria = get_user_input()

        print("\nSearching...")

        # Execute search
        cases = search_court_records(criteria)

        # Display results
        display_results(cases, criteria)

        # Show disclaimer
        print_disclaimer()

    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please try again or check your network connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
