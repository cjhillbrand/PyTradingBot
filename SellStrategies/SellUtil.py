# First I am creating the enumeration for the Sell Strategies
# This helps dictate and decipher user input.

from enum import Enum
from SellStrategies.MovingAverage import MovingAverage


class SellTypes(Enum):
    MOVING_AVG = 1
    EXP_MOVING_AVG = 2
    OTHER_SELL_STRAT = 3


def sell_type_to_string(st):
    if type(st) == int:
        st = _int_to_st(st)
    if st == SellTypes.MOVING_AVG:
        return "Moving Avg"
    if st == SellTypes.EXP_MOVING_AVG:
        return "Exponential Moving Avg"
    if st == SellTypes.OTHER_SELL_STRAT:
        return "Other Sell Strategy"


def sell_type_to_int(st):
    if st == SellTypes.MOVING_AVG:
        return 1
    if st == SellTypes.EXP_MOVING_AVG:
        return 2
    if st == SellTypes.OTHER_SELL_STRAT:
        return 3


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


def new_sell_strategy(st):
    st = _int_to_st(st)
    if st == SellTypes.MOVING_AVG:
        print("here")
        return MovingAverage()
    # TODO As you create more buy strategies fill them in here.
