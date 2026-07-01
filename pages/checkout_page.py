"""Checkout page object."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Locators and actions for checkout."""

    url = "/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.address_details_heading = page.get_by_text("Address Details", exact=True)
        self.review_order_heading = page.get_by_text("Review Your Order", exact=True)
        self.delivery_address = page.locator("#address_delivery")
        self.billing_address = page.locator("#address_invoice")
        self.order_rows = page.locator("#cart_info tbody tr")
        self.comment_textarea = page.locator("textarea[name='message']")
        self.place_order_link = page.get_by_role("link", name="Place Order")

    def load(self) -> None:
        """Open the checkout page."""
        self.navigate()

    def order_item_by_name(self, product_name: str) -> Locator:
        """Return an order review row containing the requested product name."""
        return self.order_rows.filter(has_text=product_name).first

    def place_order(self, comment: str = "Please deliver quickly.") -> None:
        """Submit the checkout comment and continue to payment."""
        self.comment_textarea.fill(comment)
        self.place_order_link.click()
