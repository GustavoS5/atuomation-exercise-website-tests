"""Shared listing page helpers for category and brand pages."""

from __future__ import annotations

from playwright.sync_api import Error, Locator, Page, TimeoutError

from pages.base_page import BasePage


class ListingPage(BasePage):
    """Common locators for category and brand product listings."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.category_heading = page.get_by_role("heading", name="CATEGORY")
        self.brands_heading = page.get_by_role("heading", name="BRANDS")
        self.title_heading = page.locator("h2.title")
        self.product_cards = page.locator(".features_items .product-image-wrapper")

    def product_card_by_name(self, product_name: str) -> Locator:
        """Return a listed product card by name."""
        return self.product_cards.filter(has_text=product_name).first

    def open_category(self, parent: str, child_href: str) -> None:
        """Open a category section and click a subcategory href."""
        self.page.locator(f"a[href='#{parent}']").click()
        child_link = self.page.locator(f"#{parent} a[href='{child_href}']")
        try:
            child_link.click(timeout=5_000)
        except TimeoutError:
            try:
                child_link.click(force=True, timeout=5_000)
            except (Error, TimeoutError):
                self.page.goto(child_href, wait_until="domcontentloaded")
        self.title_heading.wait_for(state="visible")

    def open_brand(self, brand_name: str) -> None:
        """Open a brand products page from the sidebar."""
        self.page.locator(
            f".brands-name a[href='/brand_products/{brand_name}']"
        ).click()
