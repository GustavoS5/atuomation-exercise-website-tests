"""Account registration, login, logout, and validation coverage."""

from __future__ import annotations

import re

import pytest
from faker import Faker
from pages.home_page import HomePage
from pages.signup_login_page import SignupLoginPage
from playwright.sync_api import Page, expect

from tests.helpers import (
    AccountData,
    create_account_and_continue,
    delete_current_account,
)


@pytest.mark.e2e
def test_register_user(page: Page, ui_account: AccountData) -> None:
    """A new user can register and delete the account."""
    create_account_and_continue(page, ui_account)

    delete_current_account(page)


@pytest.mark.e2e
def test_login_user_with_valid_credentials(page: Page, ui_account: AccountData) -> None:
    """A registered user can log in with valid credentials."""
    home_page = create_account_and_continue(page, ui_account)
    home_page.logout()

    signup_login_page = SignupLoginPage(page)
    expect(signup_login_page.login_heading).to_be_visible()
    signup_login_page.login(email=ui_account.email, password=ui_account.password)

    expect(HomePage(page).logged_in_as_link).to_contain_text(ui_account.name)
    delete_current_account(page)


@pytest.mark.negative
def test_login_rejects_invalid_credentials(
    signup_login_page: SignupLoginPage,
    faker: Faker,
) -> None:
    """The login form shows an error for invalid credentials."""
    expect(signup_login_page.login_heading).to_be_visible()

    signup_login_page.login(email=faker.email(), password=faker.password())

    expect(signup_login_page.invalid_login_message).to_be_visible()


@pytest.mark.e2e
def test_logout_returns_user_to_login_page(page: Page, ui_account: AccountData) -> None:
    """A logged-in user can log out and returns to the login page."""
    home_page = create_account_and_continue(page, ui_account)

    home_page.logout()

    expect(page).to_have_url(re.compile(r"/login$"))
    signup_login_page = SignupLoginPage(page)
    expect(signup_login_page.login_heading).to_be_visible()

    signup_login_page.login(email=ui_account.email, password=ui_account.password)
    delete_current_account(page)


@pytest.mark.negative
def test_signup_rejects_existing_email(page: Page, ui_account: AccountData) -> None:
    """The signup form rejects an email that already belongs to an account."""
    home_page = create_account_and_continue(page, ui_account)
    home_page.logout()

    signup_login_page = SignupLoginPage(page)
    signup_login_page.signup(name=ui_account.name, email=ui_account.email)

    expect(signup_login_page.existing_email_message).to_be_visible()

    signup_login_page.login(email=ui_account.email, password=ui_account.password)
    delete_current_account(page)
