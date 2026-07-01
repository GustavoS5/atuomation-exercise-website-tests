"""Home page object for automationexercise.com."""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from pages.cart_modal import CartModal


class HomePage(BasePage):
    """Locators and actions for the public home page."""

    url = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.hero_heading = page.get_by_role(
            "heading",
            name=re.compile("Full-Fledged practice website", re.IGNORECASE),
        ).first
        self.features_heading = page.get_by_role("heading", name="FEATURES ITEMS")
        self.product_cards = page.locator(".features_items .product-image-wrapper")
        self.recommended_items_heading = page.get_by_role(
            "heading", name="RECOMMENDED ITEMS"
        )
        self.recommended_items = page.locator(".recommended_items")
        self.scroll_up_arrow = page.locator("#scrollUp")

    def product_card_by_name(self, product_name: str) -> Locator:
        """Return a product card containing the requested product name."""
        return self.product_cards.filter(has_text=product_name).first

    def view_product_by_id(self, product_id: int) -> None:
        """Open a product detail page from the home page listing."""
        self.page.locator(f"a[href='/product_details/{product_id}']").first.click()

    def open_category(self, parent: str, child_href: str) -> None:
        """Open a category section and click a subcategory href."""
        self.page.locator(f"a[href='#{parent}']").click()
        self.page.locator(f"#{parent} a[href='{child_href}']").click()

    def add_recommended_product_to_cart_by_id(self, product_id: int) -> CartModal:
        """Add a recommended product to cart by product id."""
        self.recommended_items.locator(
            f"a.add-to-cart[data-product-id='{product_id}']"
        ).first.click()
        modal = CartModal(self.page)
        modal.wait_until_visible()
        return modal

    def scroll_to_footer(self) -> None:
        """Scroll to the shared footer area."""
        self.subscription_heading.scroll_into_view_if_needed()

    def scroll_to_top_with_arrow(self) -> None:
        """Use the floating arrow control to scroll to the page top."""
        self.scroll_up_arrow.click()

    def load(self) -> None:
        """Open the home page."""
        self.navigate()
