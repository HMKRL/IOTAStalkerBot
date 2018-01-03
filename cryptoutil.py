import json
import urllib.request
import AdvancedHTMLParser

def getSupportedCryptos():
    cryptos = [
            ('Bitcoin', 'BTC', 'bitcoin'),
            ('Ethereum', 'ETH', 'ethereum'),
            ('IOTA', 'MIOTA', 'iota'),
            ('Bitcoin Cash', 'BCH', 'bitcoin-cash'),
            ('Litecoin', 'LTC', 'litecoin'),
            ('Monero', 'XMR', 'monero'),
            ('Ripple', 'XRP', 'ripple'),
            ('Dash', 'DASH', 'dash'),
            ('Qtum', 'QTUM', 'qtum')
            ]
    return cryptos

def getPrice(crypto):
    page = urllib.request.urlopen('https://coinmarketcap.com/currencies/' + crypto).read()
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(page.decode())

    usdPrice = parser.getElementById('quote_price').getAttribute('data-usd')
    return float(usdPrice)

def getUSDTWD():
    page = urllib.request.urlopen('https://v3.exchangerate-api.com/bulk/206c492078835f2b3329cb22/USD').read()
    return float(json.loads(page.decode())['rates']['TWD'])
