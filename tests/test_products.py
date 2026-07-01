"""Product listing, product detail, search, category, brand, and review coverage."""

from __future__ import annotations

import re

import pytest
from faker import Faker
from pages.home_page import HomePage
from pages.listing_page import ListingPage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_products_listing_opens_product_detail_page(
    products_page: ProductsPage,
    page: Page,
) -> None:
    """The products listing shows products and opens a detail page."""
    expect(products_page.all_products_heading).to_be_visible()
    expect(products_page.product_cards.first).to_be_visible()

    products_page.view_product_by_id(1)
    product_detail = ProductDetailPage(page)

    expect(page).to_have_url(re.compile(r"/product_details/1$"))
    expect(product_detail.product_name).to_be_visible()
    expect(product_detail.category_text).to_contain_text("Category")
    expect(product_detail.price_text).to_contain_text("Rs.")
    expect(product_detail.availability_text).to_contain_text("Availability")
    expect(product_detail.condition_text).to_contain_text("Condition")
    expect(product_detail.brand_text).to_contain_text("Brand")


@pytest.mark.smoke
def test_search_returns_matching_products(products_page: ProductsPage) -> None:
    """Searching by product name shows matching product cards."""
    expect(products_page.all_products_heading).to_be_visible()

    products_page.search("Blue Top")

    expect(products_page.searched_products_heading).to_be_visible()
    assert products_page.visible_product_names()
    for product_name in products_page.visible_product_names():
        assert "blue top" in product_name.lower()


@pytest.mark.regression
def test_category_navigation_shows_category_products(
    home_page: HomePage,
    page: Page,
) -> None:
    """Category links navigate to the selected category product listing."""
    listing_page = ListingPage(page)
    expect(listing_page.category_heading).to_be_visible()

    home_page.open_category("Women", "/category_products/1")

    expect(listing_page.title_heading).to_have_text(
        re.compile("WOMEN - DRESS PRODUCTS", re.IGNORECASE)
    )
    expect(listing_page.product_cards.first).to_be_visible()

    home_page.load()
    home_page.open_category("Men", "/category_products/3")

    expect(listing_page.title_heading).to_have_text(
        re.compile("MEN - TSHIRTS PRODUCTS", re.IGNORECASE)
    )
    expect(listing_page.product_cards.first).to_be_visible()


@pytest.mark.regression
def test_brand_navigation_shows_brand_products(
    products_page: ProductsPage,
    page: Page,
) -> None:
    """Brand links navigate to the selected brand product listing."""
    listing_page = ListingPage(page)
    expect(listing_page.brands_heading).to_be_visible()

    products_page.open_brand("Polo")

    expect(listing_page.title_heading).to_have_text(
        re.compile("BRAND - POLO PRODUCTS", re.IGNORECASE)
    )
    expect(listing_page.product_cards.first).to_be_visible()

    listing_page.open_brand("Biba")

    expect(listing_page.title_heading).to_have_text(
        re.compile("BRAND - BIBA PRODUCTS", re.IGNORECASE)
    )
    expect(listing_page.product_cards.first).to_be_visible()


@pytest.mark.regression
def test_product_review_can_be_submitted(
    products_page: ProductsPage,
    page: Page,
    faker: Faker,
) -> None:
    """A product detail page accepts a customer review."""
    expect(products_page.all_products_heading).to_be_visible()

    products_page.view_product_by_id(1)
    product_detail = ProductDetailPage(page)

    expect(product_detail.write_review_heading).to_be_visible()
    product_detail.submit_review(
        name=faker.name(),
        email=faker.email(),
        review="This product review was submitted by an automated test.",
    )

    expect(product_detail.review_success_message).to_be_visible()
