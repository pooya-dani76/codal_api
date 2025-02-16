import requests
from bs4 import BeautifulSoup
import re


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


import time


class codalWebScraping:
    def __init__(self):
        self.baseUrl: str = "https://codal.ir/"
        self.current_page: int = 1

    def noon_30_per_page(
        self, date_from: dict, date_to: dict, length: int, current_page_number: int = 1
    ) -> dict:
        main_url: str = self.create_current_url(
            from_date=date_from, to_date=date_to, length=length, code=30
        )
        main_url: str = self.set_page_number(main_url, current_page_number)

#---------------------------------on Docker---------------------------------------
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # اجرای بدون UI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service("/usr/local/bin/chromedriver")  # استفاده از chromedriver نصب شده
#-----------------------------------on Device-------------------------------------
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # حالت بدون UI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)

        list_of_noon_30_links, last_page_number = (
            self.noon_30_links_and_last_page_number(url=main_url, driver=driver)
        )

        noon_30_information: list = self.noon_30_links_information(
            links=list_of_noon_30_links, driver=driver
        )

        driver.quit()

        all_information: dict = {
            "current_page": str(current_page_number),
            "last_page": str(last_page_number),
            "code": "noon_30",
            "date_from": date_from,
            "date_to": date_to,
            "length": str(length),
            "information": noon_30_information,
        }

        return all_information

    def noon_30_links_information(self, links: list, driver) -> list:
        final_list = []

        for link in links:
            try:
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")

                    table = soup.find("div", class_="symbol_and_name")

                    elements_to_extract = [
                        ("ctl00_txbCompanyName", "company"),
                        ("ctl00_lblListedCapital", "ListedCapital"),
                        ("ctl00_txbSymbol", "Symbol"),
                        ("ctl00_lblPeriod", "MonthlyActivityReport"),
                        ("ctl00_lblPeriodEndToDate", "PeriodEndToDate"),
                        ("ctl00_lblYearEndToDate", "YearEndToDate"),
                    ]
                    symbol_information: dict = {}
                    for element_id, label in elements_to_extract:
                        value = table.find("span", id=element_id).text.strip()
                        symbol_information[f"{label}"] = f"{value}"
                else:
                    final_list.append(
                        {
                            "error": f"you got status_code : {response.status_code} for symbol information"
                        }
                    )

            except Exception as error:
                final_list.append({"error": f"you got error {error}"})

            try:
                table_information: dict = {}
                driver.get(link)

                table_ids = ["3194", "2303", "1704"]

                table = None
                for table_id in table_ids:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, table_id))
                        )
                        table = driver.find_element(By.ID, table_id)
                        break

                    except Exception as error:
                        print(f"you got error for id {table_id} as {error}")

                if table:
                    current_table_id = table.get_attribute("id")
                    if current_table_id == "3194" or current_table_id == "2303":
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        if rows:
                            last_row = rows[-1]
                            tds = last_row.find_elements(By.TAG_NAME, "td")

                            positions = [12, 16]
                            for pos in positions:
                                if len(tds) > pos and "dynamic_comp" in tds[
                                    pos
                                ].get_attribute("class"):
                                    if pos == 12:
                                        table_information[
                                            "TotalSincetheBeginningoftheFiscalYear"
                                        ] = tds[pos].text.strip()

                                    else:
                                        table_information[
                                            "OneMonthPeriodEndingwith"
                                        ] = tds[pos].text.strip()

                                else:
                                    if pos == 12:
                                        table_information[
                                            "TotalSincetheBeginningoftheFiscalYear"
                                        ] = "not found"
                                    else:
                                        table_information[
                                            "OneMonthPeriodEndingwith"
                                        ] = "not found"

                        else:
                            table_information[
                                "TotalSincetheBeginningoftheFiscalYear"
                            ] = "not found"

                            table_information["OneMonthPeriodEndingwith"] = "not found"

                    elif current_table_id == "1704":
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        if rows:
                            last_row = rows[-1]
                            tds = last_row.find_elements(By.TAG_NAME, "td")

                            positions = [5, 6]
                            for pos in positions:
                                if len(tds) > pos and "dynamic_comp" in tds[
                                    pos
                                ].get_attribute("class"):
                                    if pos == 12:
                                        table_information[
                                            "TotalSincetheBeginningoftheFiscalYear"
                                        ] = tds[pos].text.strip()

                                    else:
                                        table_information[
                                            "OneMonthPeriodEndingwith"
                                        ] = tds[pos].text.strip()

                                else:
                                    if pos == 12:
                                        table_information[
                                            "TotalSincetheBeginningoftheFiscalYear"
                                        ] = "not found"
                                    else:
                                        table_information[
                                            "OneMonthPeriodEndingwith"
                                        ] = "not found"

                        else:
                            table_information[
                                "TotalSincetheBeginningoftheFiscalYear"
                            ] = "not found"
                            table_information["OneMonthPeriodEndingwith"] = "not found"

                else:
                    table_information["error"] = "not found eny table information"

            except Exception as error:
                table_information["error"] = f"you got error {error}"

            final_list.append(
                {
                    "symbol_information": symbol_information,
                    "table_information": table_information,
                }
            )

        return final_list

    def noon_30_links_and_last_page_number(self, url: str, driver):
        driver.get(url=url)

        # ====================  find links =====================
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "td.table__content.no-heading")
            )
        )

        links = driver.find_elements(
            By.CSS_SELECTOR, "td.table__content.no-heading a.letter-title"
        )

        links_list: list = []

        for link in links:
            href = link.get_attribute("href")
            links_list.append(href)

        # ====================  find last page number =====================
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )

        nav = driver.find_element(By.CLASS_NAME, "table-responsive")
        ul = nav.find_element(By.TAG_NAME, "ul")
        li_elements = ul.find_elements(By.TAG_NAME, "li")

        page_numbers = [int(li.text) for li in li_elements if li.text.isdigit()]
        last_page_number = max(page_numbers) if page_numbers else 1

        return links_list, last_page_number

    def create_current_url(
        self, from_date: dict, to_date: dict, length: int, code: int
    ) -> str:
        if code == 30:
            current_url = f'ReportList.aspx?search&LetterCode=%D9%86-30&LetterType=-1&FromDate={from_date["year"]}%2F{from_date["month"]}%2F{from_date["day"]}&ToDate={to_date["year"]}%2F{to_date["month"]}%2F{to_date["day"]}&AuditorRef=-1&PageNumber=index_of_page&Audited&NotAudited&IsNotAudited=false&Childs&Mains&Publisher=false&CompanyState=-1&ReportingType=-1&Length={length}&Category=-1&CompanyType=-1&Consolidatable&NotConsolidatable'
            return self.baseUrl + current_url

    def set_page_number(self, url: str, page_number: int) -> str:
        return re.sub(r"PageNumber=[^&]+", f"PageNumber={page_number}", url)

    def find_final_page(self, url: str) -> int:
        #---------------------------------on Docker---------------------------------------
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # اجرای بدون UI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/local/bin/chromedriver")  # استفاده از chromedriver نصب شده
        #-----------------------------------on Device-------------------------------------
        # service = Service(ChromeDriverManager().install())
        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # حالت بدون UI
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url=url)
        

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )

        nav = driver.find_element(By.CLASS_NAME, "table-responsive")
        ul = nav.find_element(By.TAG_NAME, "ul")
        li_elements = ul.find_elements(By.TAG_NAME, "li")

        page_numbers = [int(li.text) for li in li_elements if li.text.isdigit()]
        last_page_number = max(page_numbers) if page_numbers else None

        driver.quit()

        return last_page_number


# new: codalWebScraping = codalWebScraping()

# output = new.noon_30_per_page(
#     {"year": "1403", "month": "11", "day": "17"},
#     {"year": "1403", "month": "11", "day": "21"},
#     1,
#     1,
# )

# print(f"current_page : {output['current_page']}")
# print(f"last_page : {output['last_page']}")
# print(f"code : {output['code']}")
# print(f"date_from : {output['date_from']}")
# print(f"date_to : {output['date_to']}")
# print(f"length : {output['length']}")


# print("*************************************************************")

# for page in output["information"]:
#     print(page)
#     print("_" * 50)


