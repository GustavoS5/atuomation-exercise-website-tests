"""API tests for Automation Exercise -- covers all 14 documented endpoints.

Each test validates both the HTTP transport status and the JSON response
body using Pydantic models defined in ``tests.api_models``.

Important: the Automation Exercise API always answers with HTTP 200; the
real status is carried in the ``responseCode`` field of the JSON body.
Tests therefore assert on ``responseCode`` (via Pydantic-validated models)
rather than the HTTP status.

API reference: https://automationexercise.com/api_list
"""

from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import APIRequestContext, APIResponse

from tests.api_models import (
    AccountPayload,
    ApiResponse,
    BrandsListResponse,
    ProductsListResponse,
    SearchProductResponse,
    UserDetailResponse,
)

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _json(response: APIResponse) -> dict[str, Any]:
    """Parse an ``APIResponse`` body as a JSON dictionary."""
    data: dict[str, Any] = response.json()
    return data


# --------------------------------------------------------------------------- #
# API 1-2: Products List
# --------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.smoke
def test_api1_get_all_products_list(api_context: APIRequestContext) -> None:
    """API 1: GET /api/productsList returns 200 with all products."""
    response = api_context.get("/api/productsList")

    assert response.ok
    validated = ProductsListResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert len(validated.products) > 0
    # Every product must have the core fields populated
    for product in validated.products:
        assert product.id > 0
        assert product.name
        assert product.price
        assert product.brand
        assert product.category.category


@pytest.mark.api
@pytest.mark.negative
def test_api2_post_to_all_products_list(api_context: APIRequestContext) -> None:
    """API 2: POST /api/productsList is not supported (405)."""
    response = api_context.post("/api/productsList")

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 405
    assert validated.message == "This request method is not supported."


# --------------------------------------------------------------------------- #
# API 3-4: Brands List
# --------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.smoke
def test_api3_get_all_brands_list(api_context: APIRequestContext) -> None:
    """API 3: GET /api/brandsList returns 200 with all brands."""
    response = api_context.get("/api/brandsList")

    assert response.ok
    validated = BrandsListResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert len(validated.brands) > 0
    for brand in validated.brands:
        assert brand.id > 0
        assert brand.brand


@pytest.mark.api
@pytest.mark.negative
def test_api4_put_to_all_brands_list(api_context: APIRequestContext) -> None:
    """API 4: PUT /api/brandsList is not supported (405)."""
    response = api_context.put("/api/brandsList")

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 405
    assert validated.message == "This request method is not supported."


# --------------------------------------------------------------------------- #
# API 5-6: Search Product
# --------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.smoke
def test_api5_post_search_product(api_context: APIRequestContext) -> None:
    """API 5: POST /api/searchProduct with search_product returns 200."""
    search_term = "top"
    response = api_context.post(
        "/api/searchProduct",
        form={"search_product": search_term},
    )

    validated = SearchProductResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert len(validated.products) > 0
    # All returned products should genuinely relate to the search term
    matching = [
        p
        for p in validated.products
        if search_term in p.name.lower() or search_term in p.category.category.lower()
    ]
    assert matching, "no returned product matches the search term"


@pytest.mark.api
@pytest.mark.negative
def test_api6_search_product_without_param(api_context: APIRequestContext) -> None:
    """API 6: POST /api/searchProduct without search_product returns 400."""
    response = api_context.post("/api/searchProduct")

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 400
    assert validated.message == (
        "Bad request, search_product parameter is missing in POST request."
    )


# --------------------------------------------------------------------------- #
# API 7-10: Verify Login
# --------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.e2e
def test_api7_verify_login_valid_details(
    api_context: APIRequestContext,
    created_account: AccountPayload,
) -> None:
    """API 7: POST /api/verifyLogin with valid email+password returns 200."""
    response = api_context.post(
        "/api/verifyLogin",
        form={
            "email": created_account.email,
            "password": created_account.password,
        },
    )

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert validated.message == "User exists!"


@pytest.mark.api
@pytest.mark.negative
def test_api8_verify_login_without_email(api_context: APIRequestContext) -> None:
    """API 8: POST /api/verifyLogin without email returns 400."""
    response = api_context.post(
        "/api/verifyLogin",
        form={"password": "somepassword"},
    )

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 400
    assert validated.message == (
        "Bad request, email or password parameter is missing in POST request."
    )


@pytest.mark.api
@pytest.mark.negative
def test_api9_delete_to_verify_login(api_context: APIRequestContext) -> None:
    """API 9: DELETE /api/verifyLogin is not supported (405)."""
    response = api_context.delete("/api/verifyLogin")

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 405
    assert validated.message == "This request method is not supported."


@pytest.mark.api
@pytest.mark.negative
def test_api10_verify_login_invalid_details(api_context: APIRequestContext) -> None:
    """API 10: POST /api/verifyLogin with invalid credentials returns 404."""
    response = api_context.post(
        "/api/verifyLogin",
        form={
            "email": "nonexistent-user-invalid@example.com",
            "password": "wrongpassword",
        },
    )

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 404
    assert validated.message == "User not found!"


# --------------------------------------------------------------------------- #
# API 11-14: Account CRUD
# --------------------------------------------------------------------------- #


@pytest.mark.api
@pytest.mark.e2e
def test_api11_create_user_account(
    api_context: APIRequestContext,
    account_payload: AccountPayload,
) -> None:
    """API 11: POST /api/createAccount returns 201 with 'User created!'."""
    try:
        response = api_context.post(
            "/api/createAccount", form=account_payload.to_form()
        )

        validated = ApiResponse.model_validate(_json(response))

        assert validated.response_code == 201
        assert validated.message == "User created!"
    finally:
        # Failure-safe cleanup
        api_context.delete(
            "/api/deleteAccount",
            form={
                "email": account_payload.email,
                "password": account_payload.password,
            },
        )


@pytest.mark.api
@pytest.mark.e2e
def test_api12_delete_user_account(
    api_context: APIRequestContext,
    account_payload: AccountPayload,
) -> None:
    """API 12: DELETE /api/deleteAccount returns 200 with 'Account deleted!'."""
    # Create the account; the deletion below IS the system under test, so we
    # use ``account_payload`` (not ``created_account``) to avoid a double-delete
    # in teardown.
    api_context.post("/api/createAccount", form=account_payload.to_form())

    response = api_context.delete(
        "/api/deleteAccount",
        form={
            "email": account_payload.email,
            "password": account_payload.password,
        },
    )

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert validated.message == "Account deleted!"


@pytest.mark.api
@pytest.mark.e2e
def test_api13_update_user_account(
    api_context: APIRequestContext,
    created_account: AccountPayload,
) -> None:
    """API 13: PUT /api/updateAccount returns 200 and the change persists."""
    updated_data = created_account.model_copy(update={"name": "Updated Name"})
    response = api_context.put("/api/updateAccount", form=updated_data.to_form())

    validated = ApiResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert validated.message == "User updated!"

    # Verify the update actually persisted by re-fetching the user detail
    detail = api_context.get(
        "/api/getUserDetailByEmail",
        params={"email": created_account.email},
    )
    user = UserDetailResponse.model_validate(_json(detail)).user
    assert user.name == "Updated Name"


@pytest.mark.api
@pytest.mark.e2e
def test_api14_get_user_detail_by_email(
    api_context: APIRequestContext,
    created_account: AccountPayload,
) -> None:
    """API 14: GET /api/getUserDetailByEmail returns 200 with user detail."""
    response = api_context.get(
        "/api/getUserDetailByEmail",
        params={"email": created_account.email},
    )

    validated = UserDetailResponse.model_validate(_json(response))

    assert validated.response_code == 200
    assert validated.user.email == created_account.email
    assert validated.user.name == created_account.name
    assert validated.user.id > 0
