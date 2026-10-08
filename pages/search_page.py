import re

from playwright.sync_api import (
    Locator,
    Page,
    expect,
)

MOMO_HOME_URL = "https://www.momoshop.com.tw"


class SearchPage:
    """Page Object for momo search interactions.

    Encapsulates stable locators and essential user actions for the search feature.
    Business assertions remain within the testcases to maintain readability and intent.
    """
    PROMOTION_MODAL_DISMISS_TIMEOUT_MS = 5_000

    def __init__(self, page: Page) -> None:
        self.page = page

        # Transient promotion modal shown during homepage load
        self.promotion_modal: Locator = page.locator(".mu-z-modal")

        # Search input: momo uses input[name="search-input"] on homepage
        # and #header-search-input on the search result page.
        self.search_input: Locator = page.locator('input[name="search-input"], #header-search-input')

        # Search submit button in header
        self.search_button: Locator = page.get_by_role("button", name="搜尋", exact=True)

        # Organic search result cards and their title links
        self.product_cards: Locator = page.locator(".listAreaLi")
        self.product_titles: Locator = self.product_cards.locator("h3.prdName")
        self.product_links: Locator = self.product_titles.locator("a")

        # Organic search result product IDs
        self.product_ids: Locator = self.product_cards.locator("input[name='viewProdId']")

        # Dedicated no-result container and message text
        self.no_result_container: Locator = page.locator(".noSearchResultWrapper")
        self.no_result_text: Locator = page.locator(".noResultText")

        # Pagination components
        self.active_page_indicator: Locator = page.locator(".pagination .selected").first
        self.next_page_link: Locator = page.locator(".page-next a").first

        # Search suggestions under '猜你想搜' on homepage
        self.suggestion_items: Locator = page.get_by_test_id(
            "recommend-keywords-root"
        ).get_by_role("link")

    def goto_home(self) -> None:
        """Navigate to momo homepage."""
        self.page.goto(MOMO_HOME_URL, wait_until="domcontentloaded")
        self.promotion_modal.wait_for(
            state="hidden",
            timeout=self.PROMOTION_MODAL_DISMISS_TIMEOUT_MS,
        )

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
        """Wait for the first suggestion to be visible and non-empty, then return it."""
        suggestion = self.suggestion_items.first
        expect(suggestion).to_be_visible()
        expect(suggestion).to_have_text(re.compile(r"\S+"), use_inner_text=True)
        return suggestion.inner_text().strip(), suggestion

    def click_search_suggestion(self, suggestion_locator: Locator) -> None:
        """Click the specified search suggestion link."""
        suggestion_locator.click()

    def click_next_page(self) -> None:
        """Click the next page pagination link."""
        self.next_page_link.click()

    def get_search_input_placeholder(self) -> str:
        """Retrieve current placeholder value from search input."""
        return self.search_input.get_attribute("placeholder") or ""

    def get_organic_product_ids(self, page_number: int) -> list[str]:
        """Wait for the current cards' page links and non-empty IDs before reading them."""
        expect(self.product_cards.first).to_be_visible()
        page_link = re.compile(rf"[?&]oid={page_number}_\d+(?:&|$)")
        product_ids = []
        for index in range(self.product_cards.count()):
            expect(self.product_links.nth(index)).to_have_attribute("href", page_link)
            product_id_input = self.product_ids.nth(index)
            expect(product_id_input).to_have_value(re.compile(r"\S+"))
            product_id = product_id_input.input_value().strip()
            product_ids.append(product_id)
        return product_ids
