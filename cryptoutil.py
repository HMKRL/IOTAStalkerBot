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
    return parser.getElementById('quote_price').getAttribute('data-usd')
