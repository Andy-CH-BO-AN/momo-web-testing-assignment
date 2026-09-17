import pytest
from playwright.sync_api import expect


@pytest.fixture(autouse=True, scope="session")
def configure_playwright() -> None:
    """Configure default Playwright assertion timeout for live production network latency.

    The default 5s timeout can intermittently fail on cold container runs or peak hours
    when the momo production server takes 5-8s to return search results.
    A 15s timeout provides robust auto-waiting without adding any fixed delays.
    """
    expect.set_options(timeout=15_000)
