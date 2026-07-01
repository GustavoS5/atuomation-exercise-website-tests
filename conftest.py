"""Project-level pytest fixtures and configuration."""

from __future__ import annotations

import re

import pytest
from dotenv import load_dotenv
from faker import Faker
from playwright.sync_api import BrowserContext, Route

load_dotenv()

# Hosts that serve AdSense / Google Ads creatives, including the full-screen
# "google_vignette" overlay that intercepts pointer events during clicks.
AD_HOSTS = (
    r"googlesyndication\.com",
    r"doubleclick\.net",
    r"adservice\.google\.com",
    r"googleads\.g",
)

FAKER_SEED = 42

_AD_HOST_RE = re.compile("|".join(AD_HOSTS))


def _abort_ads(route: Route) -> None:
    """Block AdSense/Google-Ads requests; let everything else through."""
    if _AD_HOST_RE.search(route.request.url):
        route.abort("blockedbyclient")
        return
    route.continue_()


@pytest.fixture(autouse=True)
def block_ads(context: BrowserContext) -> None:
    """Abort ad/AdSense requests so vignette overlays never intercept clicks.

    automationexercise.com is ad-supported; Google AdSense injects a full-screen
    ``#google_vignette`` overlay after navigation that intercepts pointer events
    during Playwright auto-waiting clicks. Blocking the ad domains at the network
    layer prevents that iframe from ever loading.
    """
    context.route("**/*", _abort_ads)


@pytest.fixture
def faker() -> Faker:
    """A seeded Faker instance for generating realistic test data."""
    fake = Faker()
    Faker.seed(FAKER_SEED)
    return fake
