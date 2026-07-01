"""Payment and order confirmation page objects."""

from __future__ import annotations

from playwright.sync_api import Download, Page

from pages.base_page import BasePage


class PaymentPage(BasePage):
    """Locators and actions for payment."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.payment_heading = page.get_by_role("heading", name="Payment", exact=True)
        self.name_on_card_input = page.locator("input[name='name_on_card']")
        self.card_number_input = page.locator("input[name='card_number']")
        self.cvc_input = page.locator("input[name='cvc']")
        self.expiry_month_input = page.locator("input[name='expiry_month']")
        self.expiry_year_input = page.locator("input[name='expiry_year']")
        self.pay_button = page.locator("#submit")

    def pay(
        self,
        *,
        name_on_card: str,
        card_number: str = "4111111111111111",
        cvc: str = "311",
        expiry_month: str = "12",
        expiry_year: str = "2030",
    ) -> None:
        """Fill payment details and submit the order."""
        self.name_on_card_input.fill(name_on_card)
        self.card_number_input.fill(card_number)
        self.cvc_input.fill(cvc)
        self.expiry_month_input.fill(expiry_month)
        self.expiry_year_input.fill(expiry_year)
        self.pay_button.click()


class OrderPlacedPage(BasePage):
    """Locators and actions for the order placed confirmation page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.order_placed_heading = page.locator("b").filter(has_text="ORDER PLACED!")
        self.order_success_message = page.get_by_text(
            "Congratulations! Your order has been confirmed!"
        )
        self.download_invoice_link = page.get_by_role("link", name="Download Invoice")
        self.continue_link = page.get_by_role("link", name="Continue").first

    def download_invoice(self) -> Download:
        """Download the generated invoice."""
        with self.page.expect_download() as download_info:
            self.download_invoice_link.click()
        return download_info.value

    def continue_to_site(self) -> None:
        """Continue from the order placed page."""
        self.continue_link.click()
