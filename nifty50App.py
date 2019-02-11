# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()
import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import os
import json
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
element_ = driver.find_element_by_id("toDate")
button_ = driver.find_element_by_id("get")

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='fromDate', placeholder='Enter Starting Date(dd-mm-yyyy)', type='text',value="01-01-2019"),
    dcc.Input(id='toDate', placeholder='Enter End Date(dd-mm-yyyy)', type='text',value="10-02-2019"),
    dcc.Input(id="daysWindow", placeholder='Enter rolling average window', type='text',value="10"),
    dcc.Dropdown(
                id='type',
                options=[{'label':"Open Price",'value': "Open"},
                {'label':"Close Price",'value': "Close"},
                {'label':"High Price",'value': "High"}, {'label':"Low Price",'value': "Low"},
                {'label':"Shares Traded",'value': "Shares Traded"},
                {'label':"Turnover (Rs. Cr)",'value': "Turnover (Rs. Cr)"}],
                placeholder='Select from dropdown'
            ),
    html.Button('Send', id='retrainButton', style={"backgroundColor":"#FF5733"}),
    # dcc.Graph(id='table-editing-simple-output')
    dcc.Graph(id='my-graph')
])

@app.callback(
                Output('my-graph', 'figure'),
                [Input('retrainButton', 'n_clicks')],
                state=[   
                    State('fromDate', 'value'),
                    State('toDate', 'value'),
                    State('daysWindow', 'value'),
                    State('type','value')
                ]
            )
def display_output(clicks, fromDate, toDate, daysWindow,type_):
    days = int(daysWindow)
    element.clear()
    element_.clear()
    element.send_keys(fromDate)
    element_.send_keys(toDate)
    button_.click()
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
    df["Open10"] = df["Open"].rolling(days).mean()
    df["High10"] = df["High"].rolling(days).mean()
    df["Low10"] = df["Low"].rolling(days).mean()
    df["Close10"] = df["Close"].rolling(days).mean()
    df["Turnover (Rs. Cr)10"] = df["Turnover (Rs. Cr)"].rolling(days).mean()


    trace_high = go.Scatter(
    x=df.index,
    y=df[type_],
    name = str(type_)+" Price",
    line = dict(color = '#17BECF'),
    opacity = 0.8)

    trace_low = go.Scatter(
        x=df.index,
        y=df[str(type_)+"10"],
        name = str(type_)+" Price"+" Running Average with window of"+str(days)+" days",
        line = dict(color = '#7F7F7F'),
        opacity = 0.8)

    data = [trace_high,trace_low]
    fig = dict(data=data)

    return fig

app.css.append_css({"external_url": [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://codepen.io/chriddyp/pen/rzyyWo.css"
]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run_server(host='0.0.0.0', port=port,threaded = True)
