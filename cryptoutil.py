import json
import iota
import requests
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
    page = requests.post('https://coinmarketcap.com/currencies/' + crypto).content
    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseStr(page.decode())

    usdPrice = parser.getElementById('quote_price').getAttribute('data-usd')
    return float(usdPrice)

def getUSDTWD():
    page = requests.post('https://v3.exchangerate-api.com/bulk/206c492078835f2b3329cb22/USD').content
    return float(json.loads(page.decode())['rates']['TWD'])

class IOTA(object):
    __node = 'https://nodes.iota.cafe:443'
    __adapter = object()
    def __init__(self, node_protocal = 'https', node_url = 'nodes.iota.cafe', node_port = '443'):
        self.__node = node_protocal + '://' + node_url + ':' + node_port
        self.__adapter = iota.Iota(self.__node)

    def getTransactions(self, addr):
        headers = {
                'content-type': 'application/json',
                'X-IOTA-API-Version': '1'
                }
        
        command = {
                'command': 'findTransactions',
                'addresses': [addr[0:81]]
                }

        rsp = requests.post(url=self.__node, json=command, headers=headers).content
        hashes = json.loads(rsp.decode())['hashes']

        command = {
                'command': 'getTrytes',
                'hashes': hashes
                }

        rsp = requests.post(url=self.__node, json = command, headers=headers).content

        trytes = json.loads(rsp.decode())['trytes']
        
        return trytes
    
    def getNodeTime(self):
        return self.__adapter.get_node_info()
