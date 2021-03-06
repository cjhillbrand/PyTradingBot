# First I am creating the enumeration for the Sell Strategies
# This helps dictate and decipher user input.

from enum import Enum
from SellStrategies.MovingAverage import MovingAverage
from SellStrategies.LogAverage import LogAverage


class SellTypes(Enum):
    MOVING_AVG = 1
    EXP_MOVING_AVG = 2
    OTHER_SELL_STRAT = 3
    LOG_AVG = 4


def sell_type_to_string(st):
    if type(st) == int:
        st = _int_to_st(st)
    if st == SellTypes.MOVING_AVG:
        return "Moving Avg"
    if st == SellTypes.EXP_MOVING_AVG:
        return "Exponential Moving Avg"
    if st == SellTypes.OTHER_SELL_STRAT:
        return "Other Sell Strategy"
    if st == SellTypes.LOG_AVG:
        return "Log Based Average"


def sell_type_to_int(st):
    if st == SellTypes.MOVING_AVG:
        return 1
    if st == SellTypes.EXP_MOVING_AVG:
        return 2
    if st == SellTypes.OTHER_SELL_STRAT:
        return 3
    if st == SellTypes.LOG_AVG:
        return 4


def valid_st(st):
    for sto in SellTypes:
        if sell_type_to_int(sto) == st:
            return True
    return False


def _int_to_st(st):
    if st == 1:
        return SellTypes.MOVING_AVG
    if st == 2:
        return SellTypes.EXP_MOVING_AVG
    if st == 3:
        return SellTypes.OTHER_SELL_STRAT
    if st == 4:
        return SellTypes.LOG_AVG

def new_sell_strategy(st, *args):
    st = _int_to_st(st)
    if st == SellTypes.MOVING_AVG:
        if args:
            return MovingAverage(args[0], args[1])
        return MovingAverage()
    if st == SellTypes.LOG_AVG:
        return LogAverage()
    # TODO As you create more buy strategies fill them in here.
