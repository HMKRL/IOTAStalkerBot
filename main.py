#!/usr/bin/python3

import os
import json
import iota
import urllib
import qrcode
import requests
import pygraphviz

from flask import Flask
from flask import request
from io import BytesIO
from threading import Timer

import tgbot
import cryptoutil
import fsm

server_host = '140.116.245.242'
server_port = 8443

app = Flask(__name__)
bot = tgbot.Tgbot()
fsm = fsm.MyFSM()
node = cryptoutil.IOTA()
donate_addr = 'KMNGEYGMTWLCFEXSB9ZGTHNQSGUGRJRICIATMXFBDVLWHPBBQIPNXVWHARML99VVQGGMHD9VCMHIU9PXDITRHDLCWX'

last_donate_time = 0
last_donate_id = 229942559

state_track = False
track_limit = []
pre_price = 0

def initial():
    trytes = node.getTransactions('KMNGEYGMTWLCFEXSB9ZGTHNQSGUGRJRICIATMXFBDVLWHPBBQIPNXVWHARML99VVQGGMHD9VCMHIU9PXDITRHDLCWX')
    for tryte in trytes:
        transaction = iota.Transaction.from_tryte_string(tryte)
        global last_donate_time
        if tryte.find('STALKERBOTDONATE') != -1 and transaction.timestamp > last_donate_time:
            last_donate_time = transaction.timestamp
    global pre_price
    pre_price = cryptoutil.getPrice('iota')


def update():
    trytes = node.getTransactions('KMNGEYGMTWLCFEXSB9ZGTHNQSGUGRJRICIATMXFBDVLWHPBBQIPNXVWHARML99VVQGGMHD9VCMHIU9PXDITRHDLCWX')
    for tryte in trytes:
        transaction = iota.Transaction.from_tryte_string(tryte)
        global last_donate_time
        if tryte.find('STALKERBOTDONATE') != -1 and transaction.timestamp > last_donate_time and last_donate_id != 0: # donation transaction found
            print('Donation found!')
            bot.sendMessage(last_donate_id, 'Thank you for donating ' + str(transaction.value) + ' IOTA!')
            last_donate_time = transaction.timestamp

    global pre_price
    price = cryptoutil.getPrice('iota')
    print('current price:', price)
    for track_id, track_price in track_limit:
        print('id:', track_id, 'is tracking at', track_price)
        if pre_price < track_price and track_price < price:
            bot.sendMessage(track_id, 'IOTA up@' + str(track_price))
        if pre_price > track_price and track_price > price:
            bot.sendMessage(track_id, 'IOTA down@' + str(track_price))

    Timer(5.0, update).start()


@app.route('/tgWebHook', methods=['POST'])
def webhook_handler():
    chatreq = json.loads(request.data.decode())

    __import__('pprint').pprint(chatreq)

    cryptos = cryptoutil.getSupportedCryptos()

    message = chatreq.get('message')
    global state_track
    global track_limit
    if message:
        chat_id = message['chat']['id']
        msgtext = message['text']

        if msgtext == '/rate':
            keyboard = []
            row = []
            width = 3;
            for name, short, url in cryptos:
                row.append({'text': name, 'callback_data': url})
                if len(row) == width:
                    keyboard.append(list(row))
                    row.clear()
            keyboard.append(list(row))
            keyboard.append([{'text': 'advanced', 'callback_data': 'advanced'}])

            bot.sendMessage(chat_id, 'Please select crypto:', {
                'reply_markup': {
                    'inline_keyboard': keyboard,
                    }
                })
        elif msgtext == '/track':
            pass
        elif msgtext == '/remind':
            bot.sendMessage(chat_id, 'Tell me which price to remind you')
            state_track = True
            pass
        elif msgtext == '/confirm':
            pass
        elif msgtext == '/donate':
            donate_req = {
                    'address': donate_addr,
                    'amount': '',
                    'message': 'STALKERBOTDONATE',
                    'tag': 'STALKERBOTDONATE'
            }

            img = qrcode.make(json.dumps(donate_req))

            bot.sendPhoto(chat_id, tgbot.img2bytes(img))

            trytes = node.getTransactions('KMNGEYGMTWLCFEXSB9ZGTHNQSGUGRJRICIATMXFBDVLWHPBBQIPNXVWHARML99VVQGGMHD9VCMHIU9PXDITRHDLCWX')
            for tryte in trytes:
                transaction = iota.Transaction.from_tryte_string(tryte)
                global last_donate_time
                if tryte.find('STALKERBOTDONATE') != -1 and transaction.timestamp > last_donate_time:
                    last_donate_time = transaction.timestamp

            last_donate_id = chat_id

        else:
            try:
                amount = float(msgtext)
                if state_track:
                    track_limit.append((chat_id, amount))
                    state_track = False
                else:
                    fsm.setAmount(amount)
                    bot.sendMessage(chat_id, 'OK, calculate price of ' + str(amount) + ' cryptos.')

            except ValueError:
                pass

    callback_query = chatreq.get('callback_query')
    if callback_query:
        if callback_query['data'] == 'advanced':
            bot.sendMessage(callback_query['from']['id'], 'Please input crypto amount & choose fiat', {
                    'reply_markup': {
                        'inline_keyboard': [[
                            {'text': 'USD', 'callback_data': 'USD'},
                            {'text': 'TWD', 'callback_data': 'TWD'}
                        ]]
                    }
                })
            fsm.cmd_advanced()
        elif callback_query['data'] == 'USD':
            bot.sendMessage(callback_query['from']['id'], 'You have choosed USD as fiat')
            fsm.cmd_fiat(useTWD = False)
        elif callback_query['data'] == 'TWD':
            bot.sendMessage(callback_query['from']['id'], 'You have choosed TWD as fiat')
            fsm.cmd_fiat(useTWD = True)
        else:
            for name, short, url in cryptos:
                crypto = callback_query['data']
                if crypto == url:
                    fsm.cmd_crypto(crypto)
                    fsm.send(callback_query['from']['id'], short)
        bot.answerCallbackQuery(callback_query['id'])

    return "OK"

if __name__ == '__main__' :
    initial()
    fsm.get_graph().draw('state_diagram.png', prog = 'dot')
    Timer(5.0, update).start()
    app.run(host = server_host, port = server_port, debug = False, ssl_context = ('../ssl/public.pem', '../ssl/key.pem'))
