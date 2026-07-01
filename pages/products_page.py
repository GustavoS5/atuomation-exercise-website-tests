"""Products listing page object."""

from __future__ import annotations

import re
from typing import cast

from playwright.sync_api import Locator, Page, TimeoutError

from pages.base_page import BasePage
from pages.cart_modal import CartModal


class ProductsPage(BasePage):
    """Locators and actions for the all-products listing."""

    url = "/products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.all_products_heading = page.get_by_role(
            "heading", name=re.compile("ALL PRODUCTS", re.IGNORECASE)
        )
        self.searched_products_heading = page.get_by_role(
            "heading", name=re.compile("SEARCHED PRODUCTS", re.IGNORECASE)
        )
        self.search_input = page.get_by_placeholder("Search Product")
        self.search_button = page.locator("#submit_search")
        self.product_cards = page.locator(".features_items .product-image-wrapper")

    def load(self) -> None:
        """Open the products listing page."""
        self.navigate()

    def search(self, term: str) -> None:
        """Search products by name or category text."""
        self.search_input.fill(term)
        self.search_button.click()

    def product_card_by_name(self, product_name: str) -> Locator:
        """Return a product card containing the requested product name."""
        return self.product_cards.filter(has_text=product_name).first

    def view_product_by_id(self, product_id: int) -> None:
        """Open a product detail page from the listing."""
        self.page.locator(f"a[href='/product_details/{product_id}']").first.click()

    def brand_link(self, brand_name: str) -> Locator:
        """Return a brand link from the sidebar."""
        return self.page.locator(f".brands-name a[href='/brand_products/{brand_name}']")

    def open_brand(self, brand_name: str) -> None:
        """Open a brand products page from the sidebar."""
        self.brand_link(brand_name).click()

    def _add_to_cart_link_by_id(self, product_id: int) -> Locator:
        return self.page.locator(
            f"a.add-to-cart[data-product-id='{product_id}']:visible"
        ).first

    def add_product_to_cart_by_id(self, product_id: int) -> CartModal:
        """Add a product to cart from the listing by product id."""
        self._add_to_cart_link_by_id(product_id).click()
        modal = CartModal(self.page)
        modal.wait_until_visible()
        return modal

    def add_product_to_cart_by_name(self, product_name: str) -> CartModal:
        """Add a product to cart from the listing by visible product name."""
        add_to_cart_link = (
            self.product_card_by_name(product_name)
            .locator("a.add-to-cart:visible")
            .first
        )
        add_to_cart_link.click()
        modal = CartModal(self.page)
        try:
            modal.wait_until_visible(timeout=10_000)
        except TimeoutError:
            add_to_cart_link.evaluate("element => element.click()")
            modal.wait_until_visible()
        return modal

    def visible_product_names(self) -> list[str]:
        """Return visible product names from the normal product cards."""
        names = self.page.locator(".features_items .productinfo p").evaluate_all(
            """\
            elements => elements
              .filter(element => {
                const box = element.getBoundingClientRect();
                const style = window.getComputedStyle(element);
                return box.width > 0 && box.height > 0 && style.visibility !== 'hidden';
              })
              .map(element => element.innerText.trim())
              .filter(Boolean)
            """
        )
        return cast(list[str], names)
