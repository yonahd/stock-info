![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)
# stock-info

Application for scraping stock prices and information regarding the stock.

### Run in Docker
```
$ docker run -d -e STOCKS_LIST=["AAPL", "MSFT", "GOOG", "VMW"]  -p 8000:8000 ghcr.io/yonahd/stock-info:latest
```
##### Expected metrics format:
```
# HELP stock_price Stock price in USD
# TYPE stock_price gauge
stock_price{stock_symbol="MSFT"} 276.44
stock_price{stock_symbol="VMW"} 108.69
stock_price{stock_symbol="GOOG"} 2534.82
stock_price{stock_symbol="AAPL"} 150.62
# HELP stock_market_cap Stock cap in billions
# TYPE stock_market_cap gauge
stock_market_cap{stock_symbol="MSFT"} 2072.0
stock_market_cap{stock_symbol="VMW"} 45.52
stock_market_cap{stock_symbol="GOOG"} 1671.0
stock_market_cap{stock_symbol="AAPL"} 2458.0
# HELP stock_eps Stock EPS
# TYPE stock_eps gauge
stock_eps{stock_symbol="MSFT"} 9.39
stock_eps{stock_symbol="VMW"} 4.31
stock_eps{stock_symbol="GOOG"} 112.2
stock_eps{stock_symbol="AAPL"} 6.01
# HELP stock_volume Stock Volume in thousands
# TYPE stock_volume gauge
stock_volume{stock_symbol="MSFT"} 30660.747
stock_volume{stock_symbol="VMW"} 1809.282
stock_volume{stock_symbol="GOOG"} 1512.693
stock_volume{stock_symbol="AAPL"} 108732.111
```

Grafana dashboard for visualizing stock metrics:
https://grafana.com/grafana/dashboards/15956