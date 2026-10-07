import pytest
from playwright.sync_api import Page, TimeoutError

from pages.search_page import SearchPage


@pytest.mark.parametrize("pending_field", ["id", "page", "title"])
def test_product_ids_wait_for_every_rendered_card(page: Page, pending_field: str) -> None:
    """Do not return a partial or mixed-page snapshot while a later card updates."""
    page.set_content("""
        <li class="listAreaLi">
            <input name="viewProdId" value="new-1">
            <h3 class="prdName"><a href="https://example.com/product?oid=2_1">First</a></h3>
        </li>
        <li class="listAreaLi" id="pending">
            <input name="viewProdId" value="new-2">
            <h3 class="prdName"><a href="https://example.com/product?oid=2_2">Second</a></h3>
        </li>
    """)
    page.evaluate("""(field) => {
        const card = document.querySelector('#pending');
        const input = card.querySelector('input');
        const link = card.querySelector('a');
        if (field === 'id') input.value = '';
        if (field === 'page') {
            input.value = 'old-2';
            link.href = 'https://example.com/product?oid=1_2';
        }
        if (field === 'title') link.textContent = '';
        setTimeout(() => {
            input.value = 'new-2';
            link.href = 'https://example.com/product?oid=2_2';
            link.textContent = 'Second';
        }, 200);
    }""", pending_field)

    assert SearchPage(page).get_organic_product_ids(page_number=2) == ["new-1", "new-2"]


@pytest.mark.parametrize("missing_element", ["input", "h3", "li"])
def test_product_ids_do_not_hide_missing_data(page: Page, missing_element: str) -> None:
    """An incomplete card or empty list must time out instead of returning fewer IDs."""
    page.set_content("""
        <li class="listAreaLi">
            <input name="viewProdId" value="new-1">
            <h3 class="prdName"><a href="https://example.com/product?oid=2_1">First</a></h3>
        </li>
    """)
    page.locator(missing_element).evaluate("element => element.remove()")
    page.set_default_timeout(250)

    with pytest.raises(TimeoutError):
        SearchPage(page).get_organic_product_ids(page_number=2)
