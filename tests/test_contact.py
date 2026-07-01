"""Contact form coverage."""

from __future__ import annotations

from pathlib import Path

import pytest
from faker import Faker
from pages.contact_us_page import ContactUsPage
from playwright.sync_api import expect


@pytest.mark.smoke
def test_contact_form_submits_successfully(
    contact_us_page: ContactUsPage,
    faker: Faker,
    tmp_path: Path,
) -> None:
    """The contact form accepts details and an uploaded attachment."""
    upload_file = tmp_path / "contact-message.txt"
    upload_file.write_text("Automation Exercise contact form attachment.")

    expect(contact_us_page.get_in_touch_heading).to_be_visible()

    contact_us_page.fill_contact_details(
        name=faker.name(),
        email=faker.email(),
        subject="Automation Exercise contact form",
        message="This is an automated contact form test.",
    )
    contact_us_page.upload_file(upload_file)
    contact_us_page.submit_and_accept_dialog()

    expect(contact_us_page.success_message).to_contain_text(
        "Success! Your details have been submitted successfully."
    )

    contact_us_page.go_to_home()
    expect(contact_us_page.logo).to_be_visible()
