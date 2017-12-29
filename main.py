#!/usr/bin/python3

import os
import json
import urllib
import cryptoutil
import qrcode
import requests

from flask import Flask
from flask import request
from io import BytesIO

import tgbot

server_host = 'pd2a.imslab.org'
server_port = 8443

app = Flask(__name__)
bot = tgbot.Tgbot()

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
        keyboard.append(row)

        bot.sendMessage(chat_id, 'Please select a coin:', {
            'reply_markup': {
                'inline_keyboard': keyboard,
                }
            })

    callback_query = chatreq.get('callback_query')
    if callback_query:
        for name, short, url in cryptos:
            crypto = callback_query['data']
            if crypto == url:
                bot.answerCallbackQuery(callback_query['id'])
                bot.sendMessage(callback_query['from']['id'], short + '/USD: ' + str(cryptoutil.getPrice(crypto)))

    return "OK"

if __name__ == '__main__' :
    app.run(host = server_host, port = server_port, debug = False, ssl_context = ('../ssl/public.pem', '../ssl/key.pem'))
