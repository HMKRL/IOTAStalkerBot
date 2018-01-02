from transitions import State
from transitions.extensions import GraphMachine as Machine

import tgbot
import cryptoutil

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

    def calculate(self):
        result = cryptoutil.getPrice(self.__crypto)
        if self.__use_TWD:
            result = result * cryptoutil.getUSDTWD()

        result = result * self.__amount
        self.__amount = 1
        self.__use_TWD = False

        print(result)

if __name__ == '__main__' :
    fsm = MyFSM()
    fsm.cmd_crypto('iota')
    fsm.send()
    fsm.cmd_advanced()
    fsm.cmd_fiat(useTWD = True)
    fsm.cmd_amount(amount = 830)
    fsm.cmd_crypto('iota')
    fsm.send()
    fsm.cmd_amount(amount = 830)
    fsm.cmd_crypto('iota')
    fsm.send()
    fsm.get_graph().draw('state_diagram.png', prog = 'dot')
