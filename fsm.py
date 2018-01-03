from transitions import State
from transitions.extensions import GraphMachine as Machine

import tgbot
import cryptoutil

bot = tgbot.Tgbot()

states = [
    {'name': 'initial'},
    {'name': 'basic', 'on_enter': ['setCrypto'], 'on_exit': ['calculate']},
    {'name': 'advanced'},
    {'name': 'fiat', 'on_enter': ['setFiat']},
    {'name': 'amount', 'on_enter': ['setAmount']},
    {'name': 'calculate', 'on_enter': ['setCrypto'], 'on_exit': ['calculate']}
]

transitions = [
    ['cmd_advanced', 'initial', 'advanced'],
    ['cmd_crypto', 'initial', 'basic'],
    ['cmd_crypto', 'fiat', 'calculate'],
    ['cmd_crypto', 'amount', 'calculate'],
    ['cmd_fiat', 'advanced', 'fiat'],
    ['cmd_fiat', 'initial', 'fiat'],
    ['cmd_fiat', 'amount', 'fiat'],
    ['cmd_amount', 'advanced', 'amount'],
    ['cmd_amount', 'initial', 'amount'],
    ['cmd_amount', 'fiat', 'amount'],
    ['send', 'calculate', 'initial'],
    ['send', 'basic', 'initial']
]

class MyFSM(object):
    __amount = 1
    __use_TWD = False
    __crypto = cryptoutil.getSupportedCryptos()[0][2]
    def __init__(self):
        __machine = Machine(self, states = states, transitions = transitions,
            initial = 'initial', ignore_invalid_triggers = True)

    def setAmount(self, amount):
        self.__amount = amount

    def setFiat(self, useTWD):
        self.__use_TWD = useTWD

    def setCrypto(self, crypto):
        self.__crypto = crypto

    def calculate(self, chat_id, crypto_short):
        msg = str(self.__amount) + ' ' + crypto_short
        result = cryptoutil.getPrice(self.__crypto)
        if self.__use_TWD:
            msg = msg + '/TWD: '
            result = result * cryptoutil.getUSDTWD()
        else:
            msg = msg + '/USD: '

        result = result * self.__amount
        msg = msg + str(result)

        self.__amount = 1
        self.__use_TWD = False
        bot.sendMessage(chat_id, msg)
