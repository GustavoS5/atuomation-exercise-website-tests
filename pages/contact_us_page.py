"""Contact us page object."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from pages.base_page import BasePage


class ContactUsPage(BasePage):
    """Locators and actions for the contact form."""

    url = "/contact_us"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.contact_us_heading = page.get_by_role("heading", name="CONTACT US")
        self.get_in_touch_heading = page.get_by_role("heading", name="GET IN TOUCH")
        self.form = page.locator("#contact-us-form")
        # Field locators are scoped to the form; assigned after `self.form`.
        self.name_input = self.form.get_by_placeholder("Name")
        self.email_input = self.form.get_by_placeholder("Email")
        self.subject_input = self.form.get_by_placeholder("Subject")
        self.message_textarea = self.form.get_by_placeholder("Your Message Here")
        self.upload_file_input = self.form.locator("input[name='upload_file']")
        self.submit_button = self.form.locator("input[name='submit']")
        self.success_message = page.locator(".status.alert-success")

    def load(self) -> None:
        """Open the contact page."""
        self.navigate()

    def fill_contact_details(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
    ) -> None:
        """Fill the contact form fields that are always required."""
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.subject_input.fill(subject)
        self.message_textarea.fill(message)

    def upload_file(self, file_path: Path) -> None:
        """Attach a file to the contact form."""
        self.upload_file_input.set_input_files(file_path)

    def submit(self) -> None:
        """Submit the contact form."""
        self.submit_button.click()

    def submit_and_accept_dialog(self) -> None:
        """Submit the contact form and accept the browser confirmation dialog."""
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.submit()
