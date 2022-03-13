import logging
import prometheus_client as prom
import requests
import time
from bs4 import BeautifulSoup

STOCKS_LIST = ["AAPL", "MSFT", "GOOG", "S"]
MAIN_PAGE_URL = "https://finance.yahoo.com/quote/{0}?p={0}"
STOCK_PRICE_GAUGE = prom.Gauge('stock_price', 'Stock price in USD', ["stock_symbol"])
MARKET_CAP_GAUGE = prom.Gauge('stock_market_cap', 'Stock  cap in billions', ["stock_symbol"])
EPS_GAUGE = prom.Gauge('stock_eps', 'Stock EPS', ["stock_symbol"])
SYMBOL_VALUES = {'B': 1, 'T': 10 ** 3}


def get_stock_price(stock_symbol):
    resp = requests.get(MAIN_PAGE_URL.format(stock_symbol))
    soup = BeautifulSoup(resp.text, "lxml")
    price_field = soup.findAll('div', {'class': 'D(ib) Mend(20px)'})
    for div in price_field:
        rows = div.findAll('fin-streamer')
        price = rows[0].attrs['value']
        STOCK_PRICE_GAUGE.labels(stock_symbol=stock_symbol).set(price)
        logging.info("{} price: {}".format(stock_symbol, price))
        break


def get_stock_market_cap(stock_symbol):
    resp = requests.get(MAIN_PAGE_URL.format(stock_symbol))
    soup = BeautifulSoup(resp.text, "lxml")
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


def get_stock_info():
    while True:
        for stock in STOCKS_LIST:
            get_stock_market_cap(stock_symbol=stock)
            get_stock_price(stock_symbol=stock)
        time.sleep(30)


if __name__ == '__main__':
    prom.start_http_server(80)
    logging.basicConfig(level=logging.INFO)
    get_stock_info()

