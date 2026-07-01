"""Checkout, order, invoice, and cart persistence coverage."""

from __future__ import annotations

import pytest
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.signup_login_page import SignupLoginPage
from playwright.sync_api import Locator, Page, expect

from tests.helpers import (
    AccountData,
    add_first_product_and_open_cart,
    create_account_and_continue,
    delete_account_after_order,
    delete_current_account,
    place_order_from_checkout,
)


def _expect_address_matches_account(address: Locator, account: AccountData) -> None:
    expect(address).to_contain_text(account.first_name)
    expect(address).to_contain_text(account.last_name)
    expect(address).to_contain_text(account.address1)
    expect(address).to_contain_text(account.city)


@pytest.mark.e2e
def test_order_can_be_placed_after_registering_from_checkout(
    page: Page,
    ui_account: AccountData,
) -> None:
    """A shopper can register from checkout and place an order."""
    cart_page = add_first_product_and_open_cart(page)

    cart_page.proceed_to_checkout()
    cart_page.go_to_register_login_from_checkout_modal()
    create_account_and_continue(page, ui_account)

    HomePage(page).go_to_cart()
    CartPage(page).proceed_to_checkout()
    place_order_from_checkout(page, ui_account)
    delete_account_after_order(page)


@pytest.mark.e2e
def test_order_can_be_placed_after_registering_before_checkout(
    page: Page,
    ui_account: AccountData,
) -> None:
    """A registered shopper can place an order from checkout."""
    create_account_and_continue(page, ui_account)
    cart_page = add_first_product_and_open_cart(page)

    cart_page.proceed_to_checkout()
    place_order_from_checkout(page, ui_account)
    delete_account_after_order(page)


@pytest.mark.e2e
def test_order_can_be_placed_after_login_before_checkout(
    page: Page,
    ui_account: AccountData,
) -> None:
    """A returning shopper can log in and place an order."""
    home_page = create_account_and_continue(page, ui_account)
    home_page.logout()

    signup_login_page = SignupLoginPage(page)
    signup_login_page.login(email=ui_account.email, password=ui_account.password)
    expect(HomePage(page).logged_in_as_link).to_contain_text(ui_account.name)

    cart_page = add_first_product_and_open_cart(page)
    cart_page.proceed_to_checkout()
    place_order_from_checkout(page, ui_account)
    delete_account_after_order(page)


@pytest.mark.e2e
def test_searched_cart_items_persist_after_login(
    page: Page, ui_account: AccountData
) -> None:
    """Searched products added to the cart remain visible after login."""
    products_page = ProductsPage(page)
    products_page.load()

    expect(products_page.all_products_heading).to_be_visible()
    products_page.search("Blue Top")
    expect(products_page.searched_products_heading).to_be_visible()
    products_page.add_product_to_cart_by_name("Blue Top").view_cart()
    expect(CartPage(page).cart_item_by_name("Blue Top")).to_be_visible()

    CartPage(page).go_to_signup_login()
    create_account_and_continue(page, ui_account)

    HomePage(page).go_to_cart()
    expect(CartPage(page).cart_item_by_name("Blue Top")).to_be_visible()

    delete_current_account(page)


@pytest.mark.e2e
def test_checkout_addresses_match_registered_account(
    page: Page,
    ui_account: AccountData,
) -> None:
    """Checkout delivery and billing addresses match registration details."""
    create_account_and_continue(page, ui_account)

    add_first_product_and_open_cart(page).proceed_to_checkout()
    checkout_page = CheckoutPage(page)

    _expect_address_matches_account(checkout_page.delivery_address, ui_account)
    _expect_address_matches_account(checkout_page.billing_address, ui_account)

    delete_current_account(page)


@pytest.mark.e2e
def test_invoice_can_be_downloaded_after_order(
    page: Page,
    ui_account: AccountData,
) -> None:
    """An invoice can be downloaded after placing an order."""
    cart_page = add_first_product_and_open_cart(page)

    cart_page.proceed_to_checkout()
    cart_page.go_to_register_login_from_checkout_modal()
    create_account_and_continue(page, ui_account)

    HomePage(page).go_to_cart()
    CartPage(page).proceed_to_checkout()
    order_placed_page = place_order_from_checkout(page, ui_account)
    download = order_placed_page.download_invoice()

    assert download.suggested_filename

    delete_account_after_order(page)
