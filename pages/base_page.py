"""Base page object for the Playwright Page Object Model."""

from __future__ import annotations

import re

from playwright.sync_api import Page, Response


class BasePage:
    """Common state and navigation shared by every page object."""

    url: str = ""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.logo = page.get_by_alt_text("Website for automation practice")
        self.home_link = page.get_by_role("link", name=re.compile("Home"))
        self.products_link = page.locator("header a[href='/products']").first
        self.cart_link = page.locator("header a[href='/view_cart']").first
        self.signup_login_link = page.locator("header a[href='/login']").first
        self.contact_us_link = page.locator("header a[href='/contact_us']").first
        self.subscription_heading = page.get_by_role("heading", name="SUBSCRIPTION")
        self.subscription_email_input = page.get_by_placeholder("Your email address")
        self.subscribe_button = page.locator("#subscribe")

    def navigate(self) -> Response | None:
        """Open the page via `page.goto()`, resolved against `--base-url`."""
        return self.page.goto(self.url)

    @property
    def current_url(self) -> str:
        """The page's current full URL."""
        return str(self.page.url)

    def go_to_home(self) -> None:
        """Navigate to the home page from the shared header."""
        self.home_link.click()

    def go_to_products(self) -> None:
        """Navigate to the products listing from the shared header."""
        self.products_link.click()

    def go_to_cart(self) -> None:
        """Navigate to the cart from the shared header."""
        self.cart_link.click()

    def go_to_signup_login(self) -> None:
        """Navigate to the signup/login page from the shared header."""
        self.signup_login_link.click()

    def go_to_contact_us(self) -> None:
        """Navigate to the contact page from the shared header."""
        self.contact_us_link.click()
