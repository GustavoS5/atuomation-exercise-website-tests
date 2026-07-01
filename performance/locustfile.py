"""Locust load profile for the Automation Exercise public API.

Run small, polite loads against the public demo site. This is meant for learning
and trend observation, not for stress testing someone else's infrastructure.
"""

from __future__ import annotations

import logging
import os
from itertools import cycle
from typing import Any
from uuid import uuid4

from faker import Faker
from locust import HttpUser, LoadTestShape, between, events, tag, task

SEARCH_TERMS = ("top", "dress", "jeans", "shirt", "kids")

fake = Faker()


def build_account() -> dict[str, str]:
    unique_id = uuid4().hex
    first_name = fake.first_name()
    last_name = fake.last_name()

    return {
        "name": f"{first_name} {last_name}",
        "email": f"locust-{unique_id}@example.com",
        "password": fake.password(length=12),
        "title": fake.random_element(elements=("Mr", "Mrs")),
        "birth_date": str(fake.random_int(min=1, max=28)),
        "birth_month": fake.month_name(),
        "birth_year": str(fake.random_int(min=1970, max=2005)),
        "firstname": first_name,
        "lastname": last_name,
        "company": fake.company(),
        "address1": fake.street_address(),
        "address2": fake.secondary_address(),
        "country": "United States",
        "zipcode": fake.postcode(),
        "state": fake.state(),
        "city": fake.city(),
        "mobile_number": fake.msisdn()[:10],
    }


def _json_or_fail(response: Any) -> dict[str, Any] | None:
    try:
        payload = response.json()
    except ValueError:
        response.failure("response was not valid JSON")
        return None

    if not isinstance(payload, dict):
        response.failure("response JSON was not an object")
        return None

    return payload


class AutomationExerciseApiUser(HttpUser):
    """A simulated API user browsing product and brand data."""

    wait_time = between(1, 4)

    def on_start(self) -> None:
        self.search_terms = cycle(SEARCH_TERMS)

    @tag("browse", "products")
    @task(4)
    def list_products(self) -> None:
        with self.client.get(
            "/api/productsList",
            name="GET /api/productsList",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            products = payload.get("products", [])
            if payload.get("responseCode") != 200 or not products:
                response.failure("expected responseCode=200 with products")

    @tag("browse", "brands")
    @task(2)
    def list_brands(self) -> None:
        with self.client.get(
            "/api/brandsList",
            name="GET /api/brandsList",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            brands = payload.get("brands", [])
            if payload.get("responseCode") != 200 or not brands:
                response.failure("expected responseCode=200 with brands")

    @tag("browse", "search")
    @task(3)
    def search_products(self) -> None:
        search_term = next(self.search_terms)
        with self.client.post(
            "/api/searchProduct",
            data={"search_product": search_term},
            name="POST /api/searchProduct",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            if payload.get("responseCode") != 200:
                response.failure("expected responseCode=200 for product search")


class AutomationExerciseAccountUser(HttpUser):
    """A simulated API user browsing account data."""

    wait_time = between(3, 8)

    def on_start(self) -> None:
        self.account = build_account()
        self.create_account()

    def create_account(self) -> None:
        with self.client.post(
            "/api/createAccount",
            data=self.account,
            name="POST /api/createAccount",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            if payload.get("responseCode") != 201:
                response.failure("expected account creation to succeed")

    @tag("account", "login")
    @task(3)
    def verify_login(self) -> None:
        with self.client.post(
            "/api/verifyLogin",
            data={
                "email": self.account["email"],
                "password": self.account["password"],
            },
            name="POST /api/verifyLogin",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            if payload.get("responseCode") != 200:
                response.failure("expected login verification to succeed")

    @tag("account", "profile")
    @task(2)
    def get_user_details_by_email(self) -> None:
        with self.client.get(
            "/api/getUserDetailByEmail",
            params={
                "email": self.account["email"],
            },
            name="GET /api/getUserDetailByEmail",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            if payload.get("responseCode") != 200:
                response.failure("expected user details retrieval to succeed")

    @tag("account", "update")
    @task(1)
    def update_account(self) -> None:
        # Update existing account details with new data.
        self.account["name"] = "Updated Name"
        self.account["company"] = "Updated Company"
        with self.client.put(
            "/api/updateAccount",
            data=self.account,
            name="PUT /api/updateAccount",
            catch_response=True,
        ) as response:
            payload = _json_or_fail(response)
            if payload is None:
                return

            if payload.get("responseCode") != 200:
                response.failure("expected account update to succeed")

    def on_stop(self) -> None:
        self.client.delete(
            "/api/deleteAccount",
            data={"email": self.account["email"], "password": self.account["password"]},
            name="DELETE /api/deleteAccount",
        )


class LearningLoadShape(LoadTestShape):
    abstract = os.getenv("LOCUST_USE_SHAPE") != "1"

    stages = (
        (30, 1, 1.0),
        (90, 3, 1.0),
        (120, 0, 1.0),
    )

    def tick(self) -> tuple[int, float] | None:
        run_time = self.get_run_time()

        for duration, users, spawn_rate in self.stages:
            if run_time < duration:
                return users, spawn_rate

        return None


REQUEST_THRESHOLDS = {
    "GET /api/productsList": {"p95_ms": 2500, "fail_ratio": 0},
    "GET /api/brandsList": {"p95_ms": 2000, "fail_ratio": 0},
    "POST /api/searchProduct": {"p95_ms": 3000, "fail_ratio": 0},
    "POST /api/verifyLogin": {"p95_ms": 4000, "fail_ratio": 0},
    "GET /api/getUserDetailByEmail": {"p95_ms": 4000, "fail_ratio": 0},
    "PUT /api/updateAccount": {"p95_ms": 4000, "fail_ratio": 0},
}


@events.quitting.add_listener
def validate_thresholds(environment, **_kwargs: object) -> None:
    total = environment.stats.total
    p95 = total.get_response_time_percentile(0.95)

    failed = False

    if total.fail_ratio > 0:
        logging.error(
            "Load test failed: failure ratio was %.2f%%", total.fail_ratio * 100
        )
        failed = True

    if total.avg_response_time > 1000:
        logging.error(
            "Load test failed: average response time was %.0f ms",
            total.avg_response_time,
        )
        failed = True

    if p95 > 2500:
        logging.error("Load test failed: p95 response time was %.0f ms", p95)
        failed = True

    for request_name, threshold in REQUEST_THRESHOLDS.items():
        matching_stats = [
            stat
            for stat in environment.stats.entries.values()
            if stat.name == request_name
        ]

        if not matching_stats:
            continue

        request_stats = matching_stats[0]
        request_p95 = request_stats.get_response_time_percentile(0.95)

        if request_stats.fail_ratio > threshold["fail_ratio"]:
            logging.error(
                "Load test failed: %s failure ratio was %.2f%%",
                request_name,
                request_stats.fail_ratio * 100,
            )
            failed = True

        if request_p95 > threshold["p95_ms"]:
            logging.error(
                "Load test failed: %s p95 response time was %.0f ms",
                request_name,
                request_p95,
            )
            failed = True

    environment.process_exit_code = 1 if failed else 0
