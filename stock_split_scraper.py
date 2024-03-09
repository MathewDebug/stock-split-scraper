from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import yfinance as yf



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

for row in rows:
    cols = row.find_all(['th','td']) 
    cols_text = [ele.text.strip() for ele in cols]
    if len(cols_text) == 6:
        ticker, exchange, company_name, split_ratio, split_date, announcement_data = cols_text
        split_date_time = datetime.strptime(split_date, '%Y-%m-%d')    

        if split_ratio.startswith('1:') and exchange == "NASDAQ" and split_date_time >= current_date and not company_name.endswith(" ETF"):
            stock = yf.Ticker(ticker)
            stock_price = round(stock.history(period='1d')['Close'][0], 2)

            cols_text.append(stock_price)
            data.append(cols_text)

driver.quit()


for row in data:
    print("❗ Transfer Agent Verified ❗")
    print()
    print("Company: ", row[2])
    print("Stock Symbol(" + row[1] + "): **" + row[0] + "**")
    print("Ratio: ", row[3])
    print("Stock Split Date: ", row[4][5:])
    print("Current Date: ", row[5][5:])
    print("Current Price: $", row[6])
    print("---------------------")
    print("Expected Profit Per Account: $", row[6] * (int(row[3][2:]) - 1))
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

