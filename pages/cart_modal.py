"""Add-to-cart modal component."""

from __future__ import annotations

from playwright.sync_api import Page


class CartModal:
    """Actions and assertions for the cart confirmation modal."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.modal = page.locator("#cartModal")
        # Dependent locators are assigned after their parent so the chain holds.
        self.title = self.modal.get_by_text("Added!")
        self.message = self.modal.get_by_text("Your product has been added to cart.")
        self.view_cart_link = self.modal.locator("a[href='/view_cart']")
        self.continue_shopping_button = self.modal.get_by_role(
            "button", name="Continue Shopping"
        )

    def wait_until_visible(self) -> None:
        """Wait until the modal is visible after adding a product."""
        self.modal.wait_for(state="visible")

    def view_cart(self) -> None:
        """Open the cart from the confirmation modal."""
        self.view_cart_link.click()

    def continue_shopping(self) -> None:
        """Dismiss the modal and stay on the current product page."""
        self.continue_shopping_button.click()
