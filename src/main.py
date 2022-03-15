import logging
import prometheus_client as prom
import requests
import time
from bs4 import BeautifulSoup
import threading
import json
import os

MAIN_PAGE_URL = "https://finance.yahoo.com/quote/{0}?p={0}"
STOCK_PRICE_GAUGE = prom.Gauge('stock_price', 'Stock price in USD', ["stock_symbol"])
MARKET_CAP_GAUGE = prom.Gauge('stock_market_cap', 'Stock cap in billions', ["stock_symbol"])
EPS_GAUGE = prom.Gauge('stock_eps', 'Stock EPS', ["stock_symbol"])
VOLUME_GAUGE = prom.Gauge('stock_volume', 'Stock Volume in thousands', ["stock_symbol"])
SYMBOL_VALUES = {'B': 1, 'T': 10 ** 3}
user_agent_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def get_stock_price(stock_symbol, soup):
    price_field = soup.findAll('fin-streamer', {'data-field': 'regularMarketPrice', 'data-symbol': stock_symbol})
    price = float(price_field[0].text.replace(',', ''))
    STOCK_PRICE_GAUGE.labels(stock_symbol=stock_symbol).set(price)
    logging.info("{} price: {}".format(stock_symbol, price))


def get_stock_market_cap(stock_symbol, soup):
    market_cap = soup.findAll('div', {'class': 'D(ib) W(1/2) Bxz(bb) Pstart(12px) Va(t) ie-7_D(i) ie-7_Pos(a)'
                                               ' smartphone_D(b) smartphone_W(100%) smartphone_Pstart(0px)'
                                               ' smartphone_BdB smartphone_Bdc($seperatorColor)'})
    for div in market_cap:
        rows = div.findAll('tr')
        market_cap_raw = rows[0].contents[1].text
        market_cap_in_mil = float(market_cap_raw[:-1]) * SYMBOL_VALUES[market_cap_raw[-1]]
        MARKET_CAP_GAUGE.labels(stock_symbol=stock_symbol).set(market_cap_in_mil)
        logging.info("{} market cap: {}".format(stock_symbol, market_cap_in_mil))
        eps = rows[3].contents[1].text
        EPS_GAUGE.labels(stock_symbol=stock_symbol).set(float(eps))
        logging.info("{} EPS: {}".format(stock_symbol, eps))
        break


def get_stock_volume(stock_symbol, soup):
    market_cap = soup.findAll('div', {'class': 'D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b)'
                                               ' smartphone_W(100%) smartphone_Pend(0px) smartphone_BdY'
                                               ' smartphone_Bdc($seperatorColor)'})
    for div in market_cap:
        rows = div.findAll('tr')
        # Stock volume in thousands
        stock_volume = int(rows[6].contents[1].text.replace(',', '')) / 1000
        VOLUME_GAUGE.labels(stock_symbol=stock_symbol).set(stock_volume)
        logging.info("{} daily volume: {}".format(stock_symbol, stock_volume))
        break


def get_single_stock_info(stock_symbol):
    resp = requests.get(MAIN_PAGE_URL.format(stock_symbol), headers=user_agent_headers)
    soup = BeautifulSoup(resp.text, "lxml")
    get_stock_volume(stock_symbol=stock_symbol, soup=soup)
    get_stock_price(stock_symbol=stock_symbol, soup=soup)
    get_stock_market_cap(stock_symbol=stock_symbol, soup=soup)


def get_all_stock_info():
    while True:
        stocks_list = json.loads(os.environ['STOCKS_LIST'])
        threads = []

        for stock in stocks_list:
            t = threading.Thread(target=get_single_stock_info, args=[stock])
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
            get_single_stock_info(stock_symbol=stock)
        time.sleep(10)


if __name__ == '__main__':
    prom.start_http_server(8000)
    logging.basicConfig(level=logging.INFO)
    get_all_stock_info()

