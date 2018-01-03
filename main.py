#!/usr/bin/python3

import os
import json
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


def update():
    trytes = node.getTransactions('KMNGEYGMTWLCFEXSB9ZGTHNQSGUGRJRICIATMXFBDVLWHPBBQIPNXVWHARML99VVQGGMHD9VCMHIU9PXDITRHDLCWX')
    for tryte in trytes:
        if tryte.find('STALKERBOTDONATE') != -1: # donation transaction found
            pass
            

    Timer(5.0, update).start()

@app.route('/tgWebHook', methods=['POST'])
def webhook_handler():
    chatreq = json.loads(request.data.decode())

    __import__('pprint').pprint(chatreq)

    cryptos = cryptoutil.getSupportedCryptos()

    message = chatreq.get('message')
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
            pass
        elif msgtext == '/confirm':
            pass
        elif msgtext == '/donate':
            donate_req = {
                    'address': donate_addr,
                    'amount': '',
                    'message': 'STALKERBOTDONATE',
                    'tag': ''
            }

            img = qrcode.make(json.dumps(donate_req))

            bot.sendPhoto(chat_id, tgbot.img2bytes(img))

            last_donate_time = node.getNodeTime()['time']

        else:
            try:
                amount = float(msgtext)
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
    fsm.get_graph().draw('state_diagram.png', prog = 'dot')
    app.run(host = server_host, port = server_port, debug = False, ssl_context = ('../ssl/public.pem', '../ssl/key.pem'))
    Timer(5.0, update).start()
