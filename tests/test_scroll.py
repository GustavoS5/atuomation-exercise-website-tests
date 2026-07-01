"""Scroll behavior coverage."""

from __future__ import annotations

import pytest
from pages.home_page import HomePage
from playwright.sync_api import expect


@pytest.mark.regression
def test_scroll_up_arrow_returns_to_hero(home_page: HomePage) -> None:
    """The floating arrow scrolls back to the home page hero."""
    home_page.scroll_to_footer()
    expect(home_page.subscription_heading).to_be_visible()

    home_page.scroll_to_top_with_arrow()

    expect(home_page.hero_heading).to_be_visible()


@pytest.mark.regression
def test_manual_scroll_up_returns_to_hero(home_page: HomePage) -> None:
    """Manual scrolling back to the top shows the home page hero."""
    home_page.scroll_to_footer()
    expect(home_page.subscription_heading).to_be_visible()

    home_page.page.evaluate("window.scrollTo(0, 0)")

    expect(home_page.hero_heading).to_be_visible()
