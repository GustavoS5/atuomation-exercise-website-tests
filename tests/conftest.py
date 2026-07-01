"""Test-level fixtures for the Automation Exercise suite."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest
from faker import Faker
from pages.cart_page import CartPage
from pages.contact_us_page import ContactUsPage
from pages.home_page import HomePage
from pages.product_detail_page import ProductDetailPage
from pages.products_page import ProductsPage
from pages.signup_login_page import SignupLoginPage
from playwright.sync_api import APIRequestContext, Page, Playwright

from tests.api.api_models import AccountPayload

API_BASE_URL = "https://automationexercise.com"


# --------------------------------------------------------------------------- #
# UI fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def home_page(page: Page) -> HomePage:
    """A HomePage object already loaded in the browser."""
    home = HomePage(page)
    home.load()
    return home


@pytest.fixture
def products_page(page: Page) -> ProductsPage:
    """A ProductsPage object already loaded in the browser."""
    products = ProductsPage(page)
    products.load()
    return products


@pytest.fixture
def product_detail_page(page: Page) -> ProductDetailPage:
    """A ProductDetailPage object already loaded for the first product."""
    product_detail = ProductDetailPage(page)
    product_detail.load()
    return product_detail


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    """A CartPage object already loaded in the browser."""
    cart = CartPage(page)
    cart.load()
    return cart


@pytest.fixture
def signup_login_page(page: Page) -> SignupLoginPage:
    """A SignupLoginPage object already loaded in the browser."""
    signup_login = SignupLoginPage(page)
    signup_login.load()
    return signup_login


@pytest.fixture
def contact_us_page(page: Page) -> ContactUsPage:
    """A ContactUsPage object already loaded in the browser."""
    contact_us = ContactUsPage(page)
    contact_us.load()
    return contact_us


# --------------------------------------------------------------------------- #
# API fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def api_context(playwright: Playwright) -> Iterator[APIRequestContext]:
    """Session-scoped API request context pointed at Automation Exercise.

    A single context is reused across the whole run rather than one per test,
    which is faster and avoids context churn.
    """
    ctx = playwright.request.new_context(base_url=API_BASE_URL)
    yield ctx
    ctx.dispose()


@pytest.fixture
def account_payload(faker: Faker) -> AccountPayload:
    """Generate a unique, validated account payload for a single API test."""
    first_name = faker.first_name()
    last_name = faker.last_name()
    return AccountPayload(
        name=f"{first_name} {last_name}",
        email=f"api-{uuid4().hex}@example.com",
        password=f"Pwd-{uuid4().hex}!",
        title=faker.random_element(elements=("Mr", "Mrs", "Miss")),
        birth_date=str(faker.random_int(min=1, max=28)),
        birth_month=faker.month_name(),
        birth_year=str(faker.random_int(min=1970, max=2005)),
        firstname=first_name,
        lastname=last_name,
        company=faker.company(),
        address1=faker.street_address(),
        address2=faker.secondary_address(),
        country="United States",
        zipcode=faker.zipcode(),
        state=faker.state_abbr(),
        city=faker.city(),
        mobile_number=faker.numerify(text="##########"),
    )


@pytest.fixture
def created_account(
    api_context: APIRequestContext,
    account_payload: AccountPayload,
) -> Iterator[AccountPayload]:
    """Create an account via API before the test and delete it afterwards.

    Failure-safe: even if the test body raises (e.g. an ``assert`` fails), the
    ``yield`` teardown still runs ``deleteAccount`` so no test account is
    orphaned on the server.
    """
    api_context.post("/api/createAccount", form=account_payload.to_form())
    yield account_payload
    api_context.delete(
        "/api/deleteAccount",
        form={
            "email": account_payload.email,
            "password": account_payload.password,
        },
    )
