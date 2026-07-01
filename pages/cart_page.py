"""Cart page object."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """Locators and actions for the shopping cart."""

    url = "/view_cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.shopping_cart_breadcrumb = page.get_by_text("Shopping Cart", exact=True)
        self.cart_table = page.locator("#cart_info_table")
        self.cart_rows = self.cart_table.locator("tbody tr")
        self.proceed_to_checkout_link = page.locator("a.check_out")

    def load(self) -> None:
        """Open the cart page."""
        self.navigate()

    def cart_item_by_name(self, product_name: str) -> Locator:
        """Return a cart row containing the requested product name."""
        return self.cart_rows.filter(has_text=product_name).first
