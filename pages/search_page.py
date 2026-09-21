from typing import cast

from playwright.sync_api import (
    Locator,
    Page,
)
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)

MOMO_HOME_URL = "https://www.momoshop.com.tw"


class SearchPage:
    """Page Object for momo search interactions.

    Encapsulates stable locators and essential user actions for the search feature.
    Business assertions remain within the testcases to maintain readability and intent.
    """
    PROMOTION_MODAL_APPEAR_TIMEOUT_MS = 5_000

    def __init__(self, page: Page) -> None:
        self.page = page

        # Transient promotion modal shown during homepage load
        self.promotion_modal: Locator = page.locator(".mu-z-modal")

        # Search input: momo uses input[name="search-input"] on homepage
        # and #header-search-input on the search result page.
        self.search_input: Locator = page.locator('input[name="search-input"], #header-search-input')

        # Search submit button in header
        self.search_button: Locator = page.get_by_role("button", name="搜尋")

        # Organic search result product titles
        self.product_titles: Locator = page.locator(".listAreaLi h3.prdName")

        # Organic search result product IDs
        self.product_ids: Locator = page.locator(".listAreaLi input[name='viewProdId']")

        # Dedicated no-result container and message text
        self.no_result_container: Locator = page.locator(".noSearchResultWrapper")
        self.no_result_text: Locator = page.locator(".noResultText")

        # Pagination components
        self.active_page_indicator: Locator = page.locator(".pagination .pagination-link.selected").first
        self.next_page_link: Locator = page.locator(".pageArea a:has-text('下一頁')").first

        # Search suggestions under '猜你想搜' on homepage
        self.suggestion_items: Locator = page.locator(
            "ul:has(span:has-text('猜你想搜')) [data-testid='keyword-item'] a"
        )

    def goto_home(self) -> None:
        """Navigate to momo homepage after its transient promotion modal closes."""
        self.page.goto(MOMO_HOME_URL, wait_until="domcontentloaded")
        self._wait_for_promotion_modal_to_close()

    def _wait_for_promotion_modal_to_close(self) -> None:
        """Wait for momo's auto-dismissed promotion modal when it appears on homepage load."""
        try:
            self.promotion_modal.wait_for(
                state="visible",
                timeout=self.PROMOTION_MODAL_APPEAR_TIMEOUT_MS,
            )
        except PlaywrightTimeoutError:
            return

        self.promotion_modal.wait_for(state="hidden")

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

    def get_first_visible_search_suggestion(self) -> tuple[str, Locator]:
        """Find and return the text and Locator of the first visible, non-empty search suggestion.

        Raises:
            AssertionError: If no visible, non-empty search suggestion is found.
        """
        self.suggestion_items.first.wait_for(state="attached")
        count = self.suggestion_items.count()
        for index in range(count):
            candidate_locator = self.suggestion_items.nth(index)
            if candidate_locator.is_visible():
                candidate_text = candidate_locator.inner_text().strip()
                if candidate_text:
                    return candidate_text, candidate_locator

        raise AssertionError(
            "Failed to find any visible, non-empty search suggestion in '猜你想搜' section."
        )

    def click_search_suggestion(self, suggestion_locator: Locator) -> None:
        """Click the specified search suggestion link."""
        suggestion_locator.click()

    def click_next_page(self) -> None:
        """Click the next page pagination link."""
        self.next_page_link.click()

    def get_search_input_placeholder(self) -> str:
        """Retrieve current placeholder value from search input."""
        return self.search_input.get_attribute("placeholder") or ""

    def get_organic_product_ids(self) -> list[str]:
        """Extract product IDs from organic search result items in one browser call."""
        product_ids = self.product_ids.evaluate_all(
            """
            (elements) => elements
                .map((element) => element.value.trim())
                .filter(Boolean)
            """
        )
        return cast(list[str], product_ids)
