"""Test cases page object."""

from __future__ import annotations

import re

from playwright.sync_api import Page

from pages.base_page import BasePage


class TestCasesPage(BasePage):
    """Locators and actions for the published test cases page."""

    __test__ = False

    url = "/test_cases"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.test_cases_heading = page.get_by_role(
            "heading", name="Test Cases", exact=True
        )
        self.practice_list_intro = page.get_by_text(
            re.compile("Below is the list of test Cases", re.IGNORECASE)
        )

    def load(self) -> None:
        """Open the test cases page."""
        self.navigate()
