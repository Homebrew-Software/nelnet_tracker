"""Scrapes data from Nelnet's web interface."""

import datetime as dt

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# NOTE: The order of classes (which are space-separated) in XPath class
# identifiers matters. E.g. div[@class='u-grid-item u-xs-6'] is not the same as
# div[@class='u-xs-6 u-grid-item']


class NodeXPath:
    def __init__(self, xpath: str) -> None:
        self.xpath: str = xpath

    def __truediv__(self, other: "str | NodeXPath") -> "NodeXPath":
        if isinstance(other, NodeXPath):
            return NodeXPath("/".join((self.xpath, other.xpath)))
        else:
            return NodeXPath("/".join((self.xpath, other)))

    def __str__(self) -> str:
        return self.xpath

    def __repr__(self) -> str:
        return f"NodeXPath({self.xpath})"


class ElementFinder:
    def __init__(self, driver: FirefoxWebDriver) -> None:
        self.driver: FirefoxWebDriver = driver

    def find_element(self, xpath: NodeXPath) -> WebElement:
        return self.driver.find_element(By.XPATH, str(xpath))

    def find_element_text(self, xpath: NodeXPath) -> str:
        return self.find_element(xpath).text


class WebScraper:
    """Responsible for using Selenium to scrape loan data from the Nelnet
    website.
    """

    def __init__(self) -> None:
        # Web driver for interacting with Selenium's API.
        self.driver: FirefoxWebDriver = webdriver.Firefox()
        # Custom object for encapsulating element finding boilerplate.
        self.finder: ElementFinder = ElementFinder(self.driver)

    def scrape_all_data(self) -> dict:
        self.driver.get("https://nelnet.studentaid.gov/account/login")

        input('Press Enter after you have logged in and reached the "My Loans" page.')

        # Start by scraping overview data.
        main_node: NodeXPath = (
            NodeXPath("/html")
            / "body"
            / "app-root"
            / "layout-content-layout"
            / "div[@id='mainContent']"
            / "main"
            / "loan-loan-details"
            / "loan-single-account"
            / "div"
            / "div[3]"
        )

        # Wait for the main content to load.
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, str(main_node)))
        )

        data: dict = self.scrape_overview_data(main_node / "div[2]")

        # Loop through loans, collecting data.
        groups = []
        i: int = 0
        while True:
            group_xpath: NodeXPath = (
                main_node / "div[3]" / f"div[@class='ng-star-inserted'][{i+1}]"
            )
            try:
                self.finder.find_element(group_xpath)
            except NoSuchElementException:
                break

            # Scrape group data.
            group_data: dict = self.scrape_group_data(group_xpath)

            # Expand details accordion.
            loans_xpath: NodeXPath = (
                group_xpath / "u-panel-accordion" / "u-panel" / "div"
            )
            details_drop_down = self.finder.find_element(
                loans_xpath / "u-panel-header" / "span" / "button"
            )
            details_drop_down.click()
            # Wait for the accordion content to load.
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, str(loans_xpath / "div")))
            )

            # Scrape individual loan details.
            group_data["loans"] = self.scrape_individual_loans(
                loans_xpath / "div" / "div" / "div"
            )

            groups.append(group_data)
            i += 1

        data["groups"] = groups

        # Metadata.
        data["scrape_timestamp"] = str(dt.datetime.now())

        self.driver.close()

        return data

    def scrape_overview_data(self, main_node: NodeXPath) -> dict:
        finder: ElementFinder = self.finder

        # If you have some amount past due, the layout is different.
        first_div_text: str = finder.find_element_text(main_node / "div[1]" / "div[1]")
        fields: dict[str, int]
        if "past due amount" in first_div_text.lower():
            fields = dict(
                past_due_amount=2,
                monthly_payment_remaining=4,
                current_amount_due=6,
                due_date=8,
            )
        elif "current amount due" in first_div_text.lower():
            fields = dict(
                current_amount_due=2,
                due_date=6,
            )
        else:
            raise RuntimeError("Neither of the expected overview fields found.")

        data: dict[str, str] = dict.fromkeys(
            ("past_due_amount", "monthly_payment_remaining"), ""
        )
        for k, v in fields.items():
            data[k] = finder.find_element_text(main_node / "div[1]" / f"div[{v}]")
        data["current_balance"] = finder.find_element_text(
            main_node / "div[2]" / "div[2]"
        )
        data["last_payment_received"] = finder.find_element_text(
            main_node / "div[2]" / "div[6]"
        )
        return data

    def scrape_group_data(self, group_xpath: NodeXPath) -> dict:
        finder: ElementFinder = self.finder
        data_xpath: NodeXPath = group_xpath / "div"
        return dict(
            name=finder.find_element_text(group_xpath / "h2"),
            loan_type=finder.find_element_text(data_xpath / "div[1]" / "div[2]"),
            status=finder.find_element_text(data_xpath / "div[1]" / "div[4]"),
            repayment_plan=finder.find_element_text(data_xpath / "div[2]" / "div[2]"),
            payment_information=dict(
                current_amount_due=finder.find_element_text(
                    data_xpath / "div[3]" / "div[2]"
                ),
                due_date=finder.find_element_text(data_xpath / "div[3]" / "div[4]"),
                interest_rate=finder.find_element_text(
                    data_xpath / "div[3]" / "div[6]"
                ),
                regular_monthly_payment_amount=finder.find_element_text(
                    data_xpath / "div[3]" / "div[8]"
                ),
                last_payment_received=finder.find_element_text(
                    data_xpath / "div[3]" / "div[10]" / "div"
                ),
            ),
            balance_information=dict(
                principal_balance=finder.find_element_text(
                    data_xpath / "div[4]" / "div[2]"
                ),
                accrued_interest=finder.find_element_text(
                    data_xpath / "div[4]" / "div[4]"
                ),
                fees=finder.find_element_text(data_xpath / "div[4]" / "div[6]"),
                outstanding_balance=finder.find_element_text(
                    data_xpath / "div[4]" / "div[8]"
                ),
            ),
        )

    def scrape_individual_loans(self, group_loans_xpath: NodeXPath) -> list[dict]:
        finder: ElementFinder = self.finder
        loans: list[dict] = []

        i: int = 0
        while True:
            loan_xpath: NodeXPath = group_loans_xpath / f"div[{i+1}]"
            try:
                finder.find_element(loan_xpath)
            except NoSuchElementException:
                break

            loans.append(self.scrape_single_loan(loan_xpath))

            i += 1

        return loans

    def scrape_single_loan(self, loan_xpath: NodeXPath) -> dict:
        finder: ElementFinder = self.finder
        loan_data_xpath = loan_xpath / "u-card" / "u-card-content" / "div"
        data: dict = dict(
            name=finder.find_element_text(loan_xpath / "h3" / "strong"),
            group_placement=finder.find_element_text(loan_xpath / "h3" / "span"),
            loan_type=finder.find_element_text(loan_data_xpath / "div[1]" / "div[2]"),
            loan_status=finder.find_element_text(loan_data_xpath / "div[1]" / "div[4]"),
            interest_subsidy=finder.find_element_text(
                loan_data_xpath / "div[1]" / "div[6]"
            ),
            lender_name=finder.find_element_text(loan_data_xpath / "div[2]" / "div[2]"),
            school_name=finder.find_element_text(loan_data_xpath / "div[2]" / "div[4]"),
            current_information=dict(
                due_date=finder.find_element_text(
                    loan_data_xpath / "div[3]" / "div[2]"
                ),
                interest_rate=finder.find_element_text(
                    loan_data_xpath / "div[3]" / "div[4]"
                ),
                interest_rate_type=finder.find_element_text(
                    loan_data_xpath / "div[3]" / "div[4]" / "span"
                ),
                loan_term=finder.find_element_text(
                    loan_data_xpath / "div[3]" / "div[6]" / "div"
                ),
                principal_balance=finder.find_element_text(
                    loan_data_xpath / "div[4]" / "div[2]"
                ),
                accrued_interest=finder.find_element_text(
                    loan_data_xpath / "div[4]" / "div[4]"
                ),
                capitalized_interest=finder.find_element_text(
                    loan_data_xpath / "div[4]" / "div[6]"
                ),
            ),
            historic_information=dict(
                convert_to_repayment=finder.find_element_text(
                    loan_data_xpath / "div[5]" / "div[2]"
                ),
                original_loan_amount=finder.find_element_text(
                    loan_data_xpath / "div[5]" / "div[4]"
                ),
                disbursements=[],
            ),
            benefit_details=[],
        )

        i: int = 0
        while True:
            try:
                disbursement_text: str = finder.find_element_text(
                    loan_data_xpath / "div[6]" / "div[2]" / f"div[{i+1}]" / "div"
                )
            except NoSuchElementException:
                break
            data["historic_information"]["disbursements"].append(disbursement_text)
            i += 1

        benefits_tbody_xpath: NodeXPath = (
            loan_data_xpath / "div[7]" / "div[2]" / "table" / "tbody"
        )
        i: int = 0
        while True:
            row_xpath: NodeXPath = benefits_tbody_xpath / f"tr[{i+1}]"
            try:
                benefit_text: str = finder.find_element_text(row_xpath / "td[1]")
                status_text: str = finder.find_element_text(row_xpath / "td[2]")
            except NoSuchElementException:
                break
            data["benefit_details"].append((benefit_text, status_text))
            i += 1

        return data


def scrape_all_data() -> dict:
    """Scrapes all loan details from the Nelnet web interface and returns it in
    a dictionary.
    """
    scraper: WebScraper = WebScraper()
    return scraper.scrape_all_data()
