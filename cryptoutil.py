import urllib.request
import AdvancedHTMLParser

def getSupportedCryptos():
    cryptos = ['bitcoin', 'ethereum', 'ripple', 'bitcoin-cash', 'litecoin', 'iota', 'monero']
    return cryptos

def getPrice(crypto):
    page = urllib.request.urlopen('https://coinmarketcap.com/currencies/' + crypto).read()
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(page.decode())
    return parser.getElementById('quote_price').getAttribute('data-usd')
