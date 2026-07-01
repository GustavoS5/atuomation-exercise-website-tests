"""Static navigation page coverage."""

from __future__ import annotations

import re

import pytest
from pages.home_page import HomePage
from pages.test_cases_page import TestCasesPage
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_test_cases_page_is_accessible(page: Page) -> None:
    """The published Automation Exercise test cases page is accessible."""
    home_page = HomePage(page)
    home_page.load()

    home_page.go_to_test_cases()
    test_cases_page = TestCasesPage(page)

    expect(page).to_have_url(re.compile(r"/test_cases$"))
    expect(test_cases_page.test_cases_heading).to_be_visible()
    expect(test_cases_page.practice_list_intro).to_be_visible()
