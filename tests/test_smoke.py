import re
from playwright.sync_api import Page, expect

MOMO_HOME_URL = "https://www.momoshop.com.tw"


def test_momo_homepage_loads_successfully(page: Page) -> None:
    """Smoke test to verify that the browser launches and loads the momo homepage."""
    # Arrange & Act: Navigate to momo homepage
    page.goto(MOMO_HOME_URL)

    # Assert: Page title should contain 'momo'
    expect(page).to_have_title(re.compile(r"momo", re.IGNORECASE))
