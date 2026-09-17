from typing import cast

from playwright.sync_api import Locator, Page

MOMO_HOME_URL = "https://www.momoshop.com.tw"


class SearchPage:
    """Page Object for momo search interactions.

    Encapsulates stable locators and essential user actions for the search feature.
    Business assertions remain within the testcases to maintain readability and intent.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

        # Search input: momo uses input[name="search-input"] on homepage
        # and #header-search-input on the search result page.
        self.search_input: Locator = page.locator('input[name="search-input"], #header-search-input')

        # Search submit button in header
        self.search_button: Locator = page.get_by_role("button", name="搜尋")

        # Organic search result product titles
        self.product_titles: Locator = page.locator(".listAreaLi h3.prdName")

        # Dedicated no-result container and message text
        self.no_result_container: Locator = page.locator(".noSearchResultWrapper")
        self.no_result_text: Locator = page.locator(".noResultText")

        # Pagination components
        self.active_page_indicator: Locator = page.locator(".pagination .pagination-link.selected").first
        self.next_page_link: Locator = page.locator(".pageArea a:has-text('下一頁')").first

    def goto_home(self) -> None:
        """Navigate to momo homepage."""
        self.page.goto(MOMO_HOME_URL, wait_until="domcontentloaded")

    def search_by_button(self, keyword: str) -> None:
        """Fill search input and submit by clicking the search button."""
        self.search_input.fill(keyword)
        self.search_button.click()

    def search_by_enter(self, keyword: str) -> None:
        """Fill search input and submit by pressing Enter."""
        self.search_input.fill(keyword)
        self.search_input.press("Enter")

    def click_search_button(self) -> None:
        """Click search button directly without filling (e.g. for empty input scenario)."""
        self.search_button.click()

    def click_next_page(self) -> None:
        """Click the next page pagination link."""
        self.next_page_link.click()

    def get_search_input_placeholder(self) -> str:
        """Retrieve current placeholder value from search input."""
        return self.search_input.get_attribute("placeholder") or ""

    def get_organic_product_ids(self) -> list[str]:
        """Extract product IDs from organic search result items in one browser call."""
        product_ids = self.page.locator(
            ".listAreaLi input[name='viewProdId']"
        ).evaluate_all(
            """
            (elements) => elements
                .map((element) => element.value.trim())
                .filter(Boolean)
            """
        )
        return cast(list[str], product_ids)
