from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import yfinance as yf
import requests

def scrape_hedgefollow():
    '''
    Grabs all the stock of the current date in hedgefollow by comparing their announcement date
    '''
    driver = webdriver.Chrome()

    driver.get("https://hedgefollow.com/upcoming-stock-splits.php")

    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='dataTable') 
    rows = table.find_all('tr')

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date = datetime.strptime(current_date, "%Y-%m-%d")

    data = []

    # Grabs current Day Reverse Split Stock

    for row in rows:
        cols = row.find_all(['th','td']) 
        cols_text = [ele.text.strip() for ele in cols]
        if len(cols_text) == 6:
            ticker, exchange, company_name, split_ratio, split_date, announcement_data = cols_text
            split_date_time = datetime.strptime(split_date, '%Y-%m-%d')

            # Must be rever split AND be on nasdaq AND split date must be after today AND can't be etf
            if split_ratio.startswith('1:') and exchange == "NASDAQ" and split_date_time > current_date and not company_name.endswith(" ETF"):
                stock = yf.Ticker(ticker)
                stock_price = round(stock.history(period='1d')['Close'][0], 2)

                cols_text.append(stock_price)
                data.append(cols_text)

    driver.quit()
    return data

def valid_yahoo_round_up(data: list):
    '''
    Returns stocks that meets the criteria of reverse stock split on yahoo
    '''
    # Grab news articles and check content
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    confirmed_tickers = []
    manual_tickers = []

    for row in data:
        ticker = row[0]
        announcement_date = row[5]

        news_data = yf.Ticker(ticker).get_news()

        for new in news_data:
            unix_timestamp = new["providerPublishTime"]
            converted_time = datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d')

            if converted_time == announcement_date:
                link = new["link"]
                request = requests.get(link, headers=headers)
                soup = BeautifulSoup(request.content, "html.parser")
                text = soup.getText()

                if "rounded up" in text or "round up" in text or "rounding up" in text:
                    confirmed_tickers.append(row)
                else:
                    manual_tickers.append(row)

    return confirmed_tickers, manual_tickers

def format_data(data):
    for row in data:
        print("❗ Transfer Agent Verified ❗")
        print()
        print("Company: ", row[2])
        print("Stock Symbol(" + row[1] + "): **" + row[0] + "**")
        print("Ratio: ", row[3])
        print("Stock Split Date: ", row[4][5:])
        print("Current Date: ", row[5][5:])
        print("Current Price: $", str(round(row[6], 3)))
        print("---------------------")
        print("Expected Profit Per Account: $", str(round(row[6] * (int(row[3][2:]) - 1), 2)))
        print("Expected Profit for 10 Accounts: $" + str(round(row[6] * (int(row[3][2:]) - 1) * 10, 2)))
        print("Expected Profit for 20 Accounts: $" + str(round(row[6] * (int(row[3][2:]) - 1) * 20, 2)))
        print()
        print("Reminders:")
        print("We recommend to buy the stock the DAY BEFORE the stock split date")
        print("Your shares will disappear from your accounts on " + row[4][5:] + " and will reappear at the new price.")
        print()
        print("<@&1215555392294232124> <@&1215556155737112606>")
        print()
        print()
        print()

data = scrape_hedgefollow()
confirmed, manual = valid_yahoo_round_up(data)
print("------------------------------------------")
print("Confirmed: ", confirmed)
print("Manual: ", manual)
print("------------------------------------------")
# print(format_data(confirmed))
# print(format_data(manual))


