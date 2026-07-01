"""Cart and subscription coverage."""

from __future__ import annotations

import pytest
from faker import Faker
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_home_page_subscription_succeeds(home_page: HomePage, faker: Faker) -> None:
    """The home page footer subscription form shows a success message."""
    home_page.subscription_heading.scroll_into_view_if_needed()
    expect(home_page.subscription_heading).to_be_visible()

    success_message = home_page.subscribe(faker.email())

    expect(success_message).to_contain_text("You have been successfully subscribed!")


@pytest.mark.smoke
def test_cart_page_subscription_succeeds(cart_page: CartPage, faker: Faker) -> None:
    """The cart page footer subscription form shows a success message."""
    cart_page.subscription_heading.scroll_into_view_if_needed()
    expect(cart_page.subscription_heading).to_be_visible()

    success_message = cart_page.subscribe(faker.email())

    expect(success_message).to_contain_text("You have been successfully subscribed!")


@pytest.mark.regression
def test_multiple_products_can_be_added_to_cart(
    products_page: ProductsPage,
    page: Page,
) -> None:
    """Multiple products can be added and verified in the cart."""
    first_product_modal = products_page.add_product_to_cart_by_id(1)
    first_product_modal.continue_shopping()

    second_product_modal = products_page.add_product_to_cart_by_id(2)
    second_product_modal.view_cart()
    cart_page = CartPage(page)

    expect(cart_page.cart_item_by_name("Blue Top")).to_be_visible()
    expect(cart_page.item_price("Blue Top")).to_contain_text("Rs. 500")
    expect(cart_page.item_quantity("Blue Top")).to_have_text("1")
    expect(cart_page.item_total("Blue Top")).to_contain_text("Rs. 500")

    expect(cart_page.cart_item_by_name("Men Tshirt")).to_be_visible()
    expect(cart_page.item_price("Men Tshirt")).to_contain_text("Rs. 400")
    expect(cart_page.item_quantity("Men Tshirt")).to_have_text("1")
    expect(cart_page.item_total("Men Tshirt")).to_contain_text("Rs. 400")


@pytest.mark.regression
def test_product_quantity_is_preserved_in_cart(
    home_page: HomePage,
    page: Page,
) -> None:
    """A product detail quantity is reflected in the cart."""
    home_page.view_product_by_id(1)
    product_detail = ProductDetailPage(page)

    expect(product_detail.product_information).to_be_visible()
    product_detail.set_quantity(4)
    product_detail.add_to_cart().view_cart()
    cart_page = CartPage(page)

    expect(cart_page.cart_item_by_name("Blue Top")).to_be_visible()
    expect(cart_page.item_quantity("Blue Top")).to_have_text("4")


@pytest.mark.regression
def test_product_can_be_removed_from_cart(
    products_page: ProductsPage,
    page: Page,
) -> None:
    """A product can be removed from the cart."""
    modal = products_page.add_product_to_cart_by_id(1)
    modal.view_cart()
    cart_page = CartPage(page)

    expect(cart_page.cart_item_by_name("Blue Top")).to_be_visible()
    cart_page.remove_item("Blue Top")

    expect(cart_page.cart_item_by_name("Blue Top")).to_be_hidden()
    expect(cart_page.empty_cart_message).to_contain_text("Cart is empty!")


@pytest.mark.regression
def test_recommended_product_can_be_added_to_cart(
    home_page: HomePage,
    page: Page,
) -> None:
    """A recommended product can be added to the cart."""
    home_page.recommended_items_heading.scroll_into_view_if_needed()
    expect(home_page.recommended_items_heading).to_be_visible()

    home_page.add_recommended_product_to_cart_by_id(1).view_cart()

    expect(CartPage(page).cart_item_by_name("Blue Top")).to_be_visible()
