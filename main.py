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

import tgbot
import cryptoutil
import fsm

server_host = 'pd2a.imslab.org'
server_port = 8443

app = Flask(__name__)
bot = tgbot.Tgbot()
fsm = fsm.MyFSM()

def test(request):
    img = qrcode.make('https://coinmarketcap.com/coins/')

    if request.get('message'):
        chat_id = request.get('message')['chat']['id']

        bot.sendPhoto(chat_id, tgbot.img2bytes(img))

@app.route('/tgWebHook', methods=['POST'])
def webhook_handler():
    chatreq = json.loads(request.data.decode())

    __import__('pprint').pprint(chatreq)

    cryptos = cryptoutil.getSupportedCryptos()

    message = chatreq.get('message')
    if message:
        if message['text'] == '/rate':
            chat_id = message['chat']['id']
            msgtext = message['text']

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
        else:
            try:
                amount = float(message['text'])
                fsm.setAmount(amount)
            except ValueError:
                pass
            else:
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
            bot.sendMessage(callback_query['from']['id'], 'You choosed USD for fiat')
            fsm.cmd_fiat(useTWD = False)
        elif callback_query['data'] == 'TWD':
            bot.sendMessage(callback_query['from']['id'], 'You choosed TWD for fiat')
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
    app.run(host = server_host, port = server_port, debug = False, ssl_context = ('../ssl/public.pem', '../ssl/key.pem'))
