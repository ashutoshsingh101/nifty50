# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

driver = webdriver.Firefox()
driver.get("https://www.nseindia.com/products/content/equities/indices/historical_index_data.htm")

element = driver.find_element_by_id("fromDate")
element.send_keys("15-02-2018")

element_ = driver.find_element_by_id("toDate")
element_.send_keys("10-02-2019")

button_ = driver.find_element_by_id("get").click()

html_source = driver.page_source
soup = BeautifulSoup(html_source)
table = soup.find_all("div",class_="tabular-data-historic")

x = table[0].find_all("div",attrs={"id":"csvContentDiv"})
y = x[0].text
z = y.split(":")
z = list(map(lambda x: x.replace('"',""),z))
z = list(map(lambda x: re.split(",\s*",x),z))

df = pd.DataFrame(z[1:])
df.columns = z[0]
df.index = pd.to_datetime(df["Date"])

df.dropna(inplace= True)
for item in df.columns:
    if item != "Date" and item != "Shares Traded":
        df[item] = df[item].astype(float)
    elif item == "Shares Traded":
        df[item] = df[item].astype(int)
df["Open10"] = df["Open"].rolling(10).mean()
df["High10"] = df["High"].rolling(10).mean()
df["Low10"] = df["Low"].rolling(10).mean()
df["Close10"] = df["Close"].rolling(10).mean()
df["Turnover (Rs. Cr)10"] = df["Turnover (Rs. Cr)"].rolling(10).mean()