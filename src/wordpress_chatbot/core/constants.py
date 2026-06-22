from pathlib import Path

DEFAULT_PARSED_CASE_STUDIES_PATH = str(
    Path(__file__).parent.parent.parent.parent / "parsed" / "effectivesoft_portfolio_cases.csv"
)
DEFAULT_SERVICES_MD_PATH = str(Path(__file__).parent.parent.parent.parent / "parsed" / "services.md")
DEFAULT_SERVICES_URLS_PATH = str(Path(__file__).parent.parent.parent.parent / "parsed" / "services_urls.json")
DEFAULT_SERVICES_CSV_PATH = str(Path(__file__).parent.parent.parent.parent / "parsed" / "effectivesoft_services.csv")
