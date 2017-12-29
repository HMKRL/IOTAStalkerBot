"""@package tgbot
A telegram bot interface

Bot API Key should store in enviroment variable 'TG_BOT_KEY'
"""

import os
import io
import json
import requests

class Tgbot:
    __api = 'https://api.telegram.org/bot' + os.environ['TG_BOT_KEY'] + '/'

    def __init__(self):
        pass

    def getMe(self):
        return requests.post(self.__api + 'getMe')

    def sendMessage(self, chat_id, text, optional = None):
        data = {
                'chat_id': chat_id,
                'text': text
                }
        if optional:
            data.update(optional)

        return requests.post(self.__api + 'sendMessage', json = data)

    def sendPhoto(self, chat_id, photo, optional = None):
        data = {
                'chat_id': chat_id,
                }
        files = {
                'photo': photo
                }
        if optional:
            data.update(optional)

        return requests.post(self.__api + 'sendPhoto', data = data, files = files)

    def answerCallbackQuery(self, callback_query_id, optional = None):
        data = {
                'callback_query_id': callback_query_id
                }
        if optional:
            data.update(optional)

        return requests.post(self.__api + 'answerCallbackQuery', json = data)

def img2bytes(pilimg):
    """Helper function to convert image to multipart/form-data
    @param pilimg: open() or qrcode generated image
    @type  pilimg: Image

    @return: converted image
    @rtype : byte stream
    """
    byteStream = io.BytesIO()
    pilimg.save(byteStream)
    byteStream.seek(0)
    return byteStream
