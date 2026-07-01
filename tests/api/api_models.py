"""Pydantic models for validating Automation Exercise API responses.

Each model mirrors the JSON contract documented on
https://automationexercise.com/api_list and is used in the API tests to
assert both the HTTP status and the shape/payload of the response body.

Field aliases were verified against the live API so they match exactly
what the server returns (e.g. ``birth_day`` not ``birth_date``).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiResponse(BaseModel):
    """Envelope returned by simple status/message endpoints."""

    model_config = ConfigDict(extra="ignore")

    response_code: int = Field(alias="responseCode")
    message: str


class ProductCategory(BaseModel):
    """Category object nested inside a product.

    Real shape (verified against live API):
    ``{"usertype": {"usertype": "Women"}, "category": "Tops"}``
    """

    model_config = ConfigDict(extra="ignore")

    category: str


class Product(BaseModel):
    """Product object returned by the products list / search endpoints."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    name: str
    price: str
    brand: str
    category: ProductCategory


class ProductsListResponse(BaseModel):
    """Envelope for GET /api/productsList."""

    model_config = ConfigDict(extra="ignore")

    response_code: int = Field(alias="responseCode")
    products: list[Product]


class Brand(BaseModel):
    """Brand object returned by the brands list endpoint.

    Real shape (verified against live API): ``{"id": 1, "brand": "Polo"}``
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    brand: str


class BrandsListResponse(BaseModel):
    """Envelope for GET /api/brandsList."""

    model_config = ConfigDict(extra="ignore")

    response_code: int = Field(alias="responseCode")
    brands: list[Brand]


class SearchProductResponse(BaseModel):
    """Envelope for POST /api/searchProduct."""

    model_config = ConfigDict(extra="ignore")

    response_code: int = Field(alias="responseCode")
    products: list[Product] = Field(default_factory=list)


class UserDetail(BaseModel):
    """User object returned by GET /api/getUserDetailByEmail.

    Field names match the live API response exactly (verified by probing
    the endpoint):

    * The API uses ``birth_day`` -- NOT ``birth_date``.
    * The API uses ``first_name`` / ``last_name`` -- with underscores.
    * The response does NOT include ``mobile_number``.
    """

    model_config = ConfigDict(extra="ignore")

    id: int = Field(gt=0)
    name: str
    email: str
    title: str
    birth_day: str
    birth_month: str
    birth_year: str
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str


class UserDetailResponse(BaseModel):
    """Envelope for GET /api/getUserDetailByEmail."""

    model_config = ConfigDict(extra="ignore")

    response_code: int = Field(alias="responseCode")
    user: UserDetail


# --------------------------------------------------------------------------- #
# Input payload model -- symmetric validation for createAccount / updateAccount
# --------------------------------------------------------------------------- #


class AccountPayload(BaseModel):
    """Typed form payload for POST /api/createAccount & PUT /api/updateAccount.

    Using a typed model instead of a bare ``dict[str, str]`` gives symmetric
    validation: if a required field is missing or has the wrong type, the
    error surfaces at fixture-construction time rather than as a cryptic
    API failure during a test.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    email: str
    password: str
    title: str
    birth_date: str
    birth_month: str
    birth_year: str
    firstname: str
    lastname: str
    company: str
    address1: str
    address2: str
    country: str
    zipcode: str
    state: str
    city: str
    mobile_number: str

    def to_form(self) -> dict[str, str | float | bool]:
        """Serialise to a form dict suitable for ``APIRequestContext.form``."""
        return self.model_dump()
