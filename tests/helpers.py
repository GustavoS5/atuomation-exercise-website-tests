"""Reusable test workflows built on page objects."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from faker import Faker
from pages.account_information_page import AccountInformationPage
from pages.account_status_page import AccountStatusPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.payment_page import OrderPlacedPage, PaymentPage
from pages.products_page import ProductsPage
from pages.signup_login_page import SignupLoginPage
from playwright.sync_api import Page, expect


@dataclass(frozen=True)
class AccountData:
    """Account details for account-based scenarios."""

    name: str
    email: str
    password: str
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str
    mobile_number: str


def make_account_data(faker: Faker) -> AccountData:
    """Create unique account data so tests can register/delete independently."""
    first_name = faker.first_name()
    last_name = faker.last_name()
    return AccountData(
        name=f"{first_name} {last_name}",
        email=f"testuser-{uuid4().hex}@example.com",
        password=f"Pwd-{uuid4().hex}!",
        first_name=first_name,
        last_name=last_name,
        company="Example Corp",
        address1="1 Test Street",
        address2="Suite 2",
        country="United States",
        state="CA",
        city="San Francisco",
        zipcode="94105",
        mobile_number="5551234567",
    )


def create_account(page: Page, account: AccountData) -> AccountStatusPage:
    """Create an account from the signup page and return the status page."""
    signup_login_page = SignupLoginPage(page)
    signup_login_page.load()
    signup_login_page.signup(name=account.name, email=account.email)

    account_information_page = AccountInformationPage(page)
    expect(account_information_page.heading).to_be_visible()
    account_information_page.fill_required_account_details(
        password=account.password,
        first_name=account.first_name,
        last_name=account.last_name,
        company=account.company,
        address1=account.address1,
        address2=account.address2,
        country=account.country,
        state=account.state,
        city=account.city,
        zipcode=account.zipcode,
        mobile_number=account.mobile_number,
    )
    account_information_page.create_account()
    return AccountStatusPage(page)


def create_account_and_continue(page: Page, account: AccountData) -> HomePage:
    """Create an account, verify creation, and continue into the site."""
    account_status_page = create_account(page, account)
    expect(account_status_page.account_created_heading).to_be_visible()
    account_status_page.continue_to_site()

    home_page = HomePage(page)
    expect(home_page.logged_in_as_link).to_contain_text(account.name)
    return home_page


def delete_current_account(page: Page) -> AccountStatusPage:
    """Delete the currently logged-in account and return the status page."""
    HomePage(page).delete_account()
    account_status_page = AccountStatusPage(page)
    expect(account_status_page.account_deleted_heading).to_be_visible()
    return account_status_page


def add_first_product_and_open_cart(page: Page) -> CartPage:
    """Add Blue Top from the products page and open the cart."""
    products_page = ProductsPage(page)
    products_page.load()
    products_page.add_product_to_cart_by_name("Blue Top").view_cart()

    cart_page = CartPage(page)
    expect(cart_page.cart_item_by_name("Blue Top")).to_be_visible()
    return cart_page


def place_order_from_checkout(page: Page, account: AccountData) -> OrderPlacedPage:
    """Complete checkout and payment from an open checkout page."""
    checkout_page = CheckoutPage(page)
    expect(checkout_page.address_details_heading).to_be_visible()
    expect(checkout_page.review_order_heading).to_be_visible()
    checkout_page.place_order()

    payment_page = PaymentPage(page)
    expect(payment_page.payment_heading).to_be_visible()
    payment_page.pay(name_on_card=account.name)

    order_placed_page = OrderPlacedPage(page)
    expect(order_placed_page.order_placed_heading).to_be_visible()
    return order_placed_page


def delete_account_after_order(page: Page) -> None:
    """Continue from order confirmation, then delete the logged-in account."""
    OrderPlacedPage(page).continue_to_site()
    delete_current_account(page)
