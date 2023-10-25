"""The main script. Useful for debugging."""

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def main():
    driver = webdriver.Firefox()
    driver.get("https://secure.nelnet.com/account/login")

    input("Press Enter after you have logged in.")

    driver.get("https://secure.nelnet.com/loan-details")

    # Loop through loans, collecting data.
    xp_main = "//div[@id='mainContent']"
    data: dict = scrape_overview_data(driver, xp_main)
    groups = []
    i = 0
    while True:
        try:
            el = driver.find_element(
                By.XPATH, f"{xp_main}//div[@class='ng-star-inserted'][{i+1}]"
            )
        except NoSuchElementException:
            break
        # Expand the details accordion.
        details_drop_down = driver.find_element(
            By.XPATH,
            f"{xp_main}//button[@class='u-panel-button u-button ng-star-inserted'][{i+1}]",
        )
        details_drop_down.click()

        # Scrape the data.
        groups.append(scrape_group_data(driver, xp_main, i))
        i += 1

    data["groups"] = groups

    driver.close()


# NOTE: The order of classes (which are space-separated) in XPath class
# identifiers matters. E.g. div[@class='u-grid-item u-xs-6'] is not the same as
# div[@class='u-xs-6 u-grid-item']


def scrape_overview_data(driver: FirefoxWebDriver, xpath_main: str) -> dict:
    return dict(
        current_amount_due=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-item u-grid-container u-sm-12 u-md-6 u-pr-xs-0 u-pr-sm-1 u-pr-md-2']/div[@class='u-grid-item u-xs-6 u-typography-align--right']",
        ).text,
        due_date=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-item u-grid-container u-sm-12 u-md-6 u-pr-xs-0 u-pr-sm-1 u-pr-md-2']/div[@class='u-grid-item u-xs-6 u-typography-align--right ng-star-inserted']",
        ).text,
        current_balance=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-item u-grid-container u-sm-12 u-md-6 u-pl-xs-0 u-pr-sm-1']/div[@class='u-grid-item u-xs-6 u-typography-align--right'][1]",
        ).text,
        last_payment_received=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-item u-grid-container u-sm-12 u-md-6 u-pl-xs-0 u-pr-sm-1']/div[@class='u-grid-item u-xs-6 u-typography-align--right'][2]",
        ).text,
    )


def scrape_group_data(driver: FirefoxWebDriver, xpath_main: str, i: int) -> dict:
    return dict(
        group=driver.find_element(
            By.XPATH, f"{xpath_main}//div[@class='ng-star-inserted'][1]/h2[1]"
        ).text,
        loan_type=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-container'][1]/div[@class='ng-star-inserted']/div[@class='u-grid-item u-grid-container u-xs-12 u-mb-xs-1 u-paper']/div[@class='u-grid-item u-grid-container u-xs-12 u-sm-12 u-md-6 u-pr-xs-0 u-pr-sm-1 u-pr-md-2']/div[@class='u-grid-item u-xs-6 u-typography-align--right'][1]",
        ).text,
        status=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-container'][1]/div[@class='ng-star-inserted']/div[@class='u-grid-item u-grid-container u-xs-12 u-mb-xs-1 u-paper']/div[@class='u-grid-item u-grid-container u-xs-12 u-sm-12 u-md-6 u-pr-xs-0 u-pr-sm-1 u-pr-md-2']/div[@class='u-grid-item u-xs-6 u-typography-align--right'][2]",
        ).text,
        repayment_plan=driver.find_element(
            By.XPATH,
            f"{xpath_main}//div[@class='u-grid-container'][1]/div[@class='ng-star-inserted']/div[@class='u-grid-item u-grid-container u-xs-12 u-mb-xs-1 u-paper']/div[@class='u-grid-item u-grid-container u-xs-12 u-sm-12 u-md-6 u-pr-xs-0 u-pr-sm-1']/p[@class='u-grid-item u-xs-6 u-typography-align--right ng-star-inserted']",
        ).text,
        payment_information=dict(
            current_amount_due="$0.00",
            due_date="02/02/2024",
            interest_rate="3.400%",
            last_payment_received="$50.49 on 08/21/2017",
        ),
        balance_information=dict(
            principal_balance="$4794.32",
            accrued_interest="$125.41",
            fees="",
            outstanding_balance="",
        ),
    )


if __name__ == "__main__":
    main()
