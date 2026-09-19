import re
from urllib.parse import quote

import pytest
from playwright.sync_api import Page, expect

from pages.search_page import SearchPage


def _search_path(query: str) -> str:
    """Build momo's URL-encoded search path for a query."""
    return f"/search/{quote(query, safe='')}"


def test_search_normal_keyword_with_button(page: Page) -> None:
    """Verify that searching a normal keyword via the Search button successfully loads results."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    keyword = "iphone"

    # Act: Search using the Search button
    search_page.search_by_button(keyword)

    # Assert: Result page loaded, products visible, and results contain keyword
    expect(page).to_have_url(re.compile(rf"{re.escape(_search_path(keyword))}(?:\?|$)"))
    expect(search_page.product_titles.first).to_be_visible()
    expect(search_page.search_input).to_have_value(keyword)
    titles = search_page.product_titles.all_inner_texts()

    failed_results = [
        (index, title)
        for index, title in enumerate(titles, start=1)
        if keyword.lower() not in title.lower()
    ]
    assert not failed_results, (
        f"Expected every product title to contain '{keyword}' (case-insensitive).\n"
        f"Non-matching result indexes: {[idx for idx, _ in failed_results]}.\n"
        f"Sample non-matching titles: {[title for _, title in failed_results[:5]]}"
    )


def test_search_multi_keyword_with_enter(page: Page) -> None:
    """Verify that multi-keyword search submitted via Enter returns products matching all tokens."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    query = "iphone 17系列"
    required_keywords = re.findall(r"[A-Za-z]+|\d+|[\u4e00-\u9fff]+", query)

    # Act: Search using Enter key
    search_page.search_by_enter(query)

    # Assert: Result page loaded, products visible, and query state preserved
    expect(page).to_have_url(re.compile(rf"{re.escape(_search_path(query))}(?:\?|$)"))
    expect(search_page.product_titles.first).to_be_visible()
    expect(search_page.search_input).to_have_value(query)

    titles = search_page.product_titles.all_inner_texts()

    matching_results = [
        title
        for title in titles
        if all(
            keyword.lower() in title.lower()
            for keyword in required_keywords
        )
    ]
    assert matching_results, (
        f"Expected at least one product title containing all keywords "
        f"{required_keywords}. "
        f"Sample titles: {titles[:5]}"
    )


def test_search_no_result(page: Page) -> None:
    """Verify that searching for a non-existent keyword displays the clear no-result state."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    no_result_keyword = "123qweasdzxc"
    expected_no_result_text = (
        f'很抱歉，查無 "{no_result_keyword}"的相關商品，您可以調整關鍵字試試看'
    )

    # Act: Search for non-existent keyword
    search_page.search_by_button(no_result_keyword)

    # Assert: Result page displays the exact no-result message and zero organic products
    expect(page).to_have_url(
        re.compile(rf"{re.escape(_search_path(no_result_keyword))}(?:\?|$)")
    )
    expect(search_page.no_result_container).to_be_visible()
    expect(search_page.search_input).to_have_value(no_result_keyword)
    expect(search_page.no_result_text).to_have_text(expected_no_result_text)
    expect(search_page.product_titles).to_have_count(0)


def test_search_pagination(page: Page) -> None:
    """Verify that pagination preserves search context and partitions organic products correctly."""
    # Arrange: Perform initial search and capture page 1 state
    search_page = SearchPage(page)
    search_page.goto_home()
    keyword = "iphone"
    search_page.search_by_button(keyword)

    expect(search_page.product_titles.first).to_be_visible()
    expect(search_page.active_page_indicator).to_have_text("1")
    page_1_url = page.url

    page_1_product_ids = search_page.get_organic_product_ids()
    assert page_1_product_ids, "Expected organic products on page 1"
    assert len(page_1_product_ids) == len(set(page_1_product_ids)), (
        "Pagination result integrity error: duplicate product IDs found within Page 1"
    )
    page_1_first_product_id = page_1_product_ids[0]

    # Act: Click next page pagination control
    search_page.click_next_page()

    # Assert: Active page changes to 2, query state remains, and second page products load
    expect(search_page.active_page_indicator).to_have_text("2")
    expect(search_page.search_input).to_have_value(keyword)
    expect(search_page.product_ids.first).not_to_have_value(page_1_first_product_id)

    page_2_product_ids = search_page.get_organic_product_ids()
    assert page_2_product_ids, "Expected organic products on page 2"
    assert len(page_2_product_ids) == len(set(page_2_product_ids)), (
        "Pagination result integrity error: duplicate product IDs found within Page 2"
    )

    duplicate_ids = set(page_1_product_ids).intersection(page_2_product_ids)
    assert not duplicate_ids, (
        "Pagination result partition error: duplicate product IDs found between Page 1 and Page 2: "
        f"{duplicate_ids}"
    )

    assert page.url != page_1_url, f"Page URL did not change after pagination: {page.url}"


def test_search_special_character(page: Page) -> None:
    """Verify that searching with special character retains query state and returns matching products."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    query = "iphone+"

    # Act: Submit search with special character
    search_page.search_by_button(query)

    # Assert: Query state preserves 'iphone+' and results include an iPhone-related product
    expect(page).to_have_url(re.compile(rf"{re.escape(_search_path(query))}(?:\?|$)"))
    expect(search_page.product_titles.first).to_be_visible()
    expect(search_page.search_input).to_have_value(query)
    titles = search_page.product_titles.all_inner_texts()

    has_matching_title = any("iphone" in title.lower() for title in titles)
    assert has_matching_title, (
        "Expected at least one product title containing 'iphone', "
        f"got titles: {titles[:5]}"
    )



@pytest.mark.parametrize(
    "suggestion",
    [
        "iPhone 18 Pro Max",
        "17 Pro Max 透明殼",
    ],
)
def test_search_suggestion(page: Page, suggestion: str) -> None:
    """Verify that clicking a search suggestion applies the same relevance rules as typed queries."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    required_keywords = re.findall(r"[A-Za-z]+|\d+|[\u4e00-\u9fff]+", suggestion)

    # Act: Click a "猜你想搜" suggestion
    search_page.click_search_suggestion(suggestion)

    # Assert: Suggestion becomes the active query and returns relevant organic results
    expect(page).to_have_url(re.compile(rf"{re.escape(_search_path(suggestion))}(?:\?|$)"))
    expect(search_page.product_titles.first).to_be_visible()
    expect(search_page.search_input).to_have_value(suggestion)
    titles = search_page.product_titles.all_inner_texts()

    if len(required_keywords) == 1:
        keyword = required_keywords[0]
        failed_results = [
            (index, title)
            for index, title in enumerate(titles, start=1)
            if keyword.lower() not in title.lower()
        ]
        assert not failed_results, (
            f"Expected every product title to contain '{keyword}' (case-insensitive).\n"
            f"Non-matching result indexes: {[idx for idx, _ in failed_results]}.\n"
            f"Sample non-matching titles: {[title for _, title in failed_results[:5]]}"
        )
    else:
        matching_results = [
            title
            for title in titles
            if all(keyword.lower() in title.lower() for keyword in required_keywords)
        ]
        assert matching_results, (
            "Expected at least one product title containing all keywords "
            f"{required_keywords}. Sample titles: {titles[:5]}"
        )


def test_search_empty_input_with_enter(page: Page) -> None:
    """Verify that pressing Enter with an empty search input does not trigger a search."""
    # Arrange: Navigate to momo homepage with an empty search input
    search_page = SearchPage(page)
    search_page.goto_home()
    expect(search_page.search_input).to_have_value("")
    home_url = page.url

    # Act: Press Enter without entering a keyword
    search_page.press_enter()

    # Assert: No search navigation occurs and the input remains empty
    expect(page).to_have_url(home_url)
    expect(search_page.search_input).to_have_value("")


def test_search_empty_input_with_button(page: Page) -> None:
    """Verify that submitting an empty input via Search button uses the active placeholder keyword."""
    # Arrange: Navigate to momo homepage and wait for a non-empty dynamic placeholder
    search_page = SearchPage(page)
    search_page.goto_home()

    expect(search_page.search_input).to_have_attribute("placeholder", re.compile(r"\S+"))
    expect(search_page.search_input).to_have_value("")
    placeholder = search_page.get_search_input_placeholder()

    # Act: Click Search button without entering any text
    search_page.click_search_button()

    # Assert: Search uses the current placeholder keyword
    expect(page).to_have_url(
        re.compile(rf"{re.escape(_search_path(placeholder))}(?:\?|$)")
    )
    expect(search_page.search_input).to_have_value(placeholder)


def test_search_whitespace_only_input(page: Page) -> None:
    """Verify that submitting whitespace-only input enters no-result state without crashing."""
    # Arrange: Navigate to momo homepage
    search_page = SearchPage(page)
    search_page.goto_home()
    whitespace_query = "   "
    expected_no_result_text = (
        f'很抱歉，查無 "{whitespace_query}"的相關商品，您可以調整關鍵字試試看'
    )

    # Act: Search with whitespace-only input
    search_page.search_by_button(whitespace_query)

    # Assert: Results page enters no-result state with zero organic products and no crash
    expect(page).to_have_url(
        re.compile(rf"{re.escape(_search_path(whitespace_query))}(?:\?|$)")
    )
    expect(search_page.no_result_container).to_be_visible()
    expect(search_page.no_result_text).to_have_text(expected_no_result_text)
    expect(search_page.product_titles).to_have_count(0)
