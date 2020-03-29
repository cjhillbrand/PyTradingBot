from enum import Enum
from BuyStrategies.MovingAverage import MovingAverage


class BuyTypes(Enum):
    MOVING_AVG = 1
    EXP_MOVING_AVG = 2
    OTHER_BUY_STRAT = 3


def buy_type_to_string(bt):
    if type(bt) == int:
        bt = _int_to_bt(bt)
    if bt == BuyTypes.MOVING_AVG:
        return "Moving Avg"
    if bt == BuyTypes.EXP_MOVING_AVG:
        return "Exponential Moving Avg"
    if bt == BuyTypes.OTHER_BUY_STRAT:
        return "Other Buy Strategy"


def buy_type_to_int(bt):
    if bt == BuyTypes.MOVING_AVG:
        return 1
    if bt == BuyTypes.EXP_MOVING_AVG:
        return 2
    if bt == BuyTypes.OTHER_BUY_STRAT:
        return 3


def valid_bt(bt):
    for bto in BuyTypes:
        if buy_type_to_int(bto) == bt:
            return True
    return False


def _int_to_bt(bt):
    if bt == 1:
        return BuyTypes.MOVING_AVG
    if bt == 2:
        return BuyTypes.EXP_MOVING_AVG
    if bt == 3:
        return BuyTypes.OTHER_BUY_STRAT


def new_buy_strategy(bt, *args):
    bt = _int_to_bt(bt)
    if bt == BuyTypes.MOVING_AVG:
        if args:
            return MovingAverage(args[0], args[1])
        return MovingAverage()
    # TODO As you create more buy strategies fill them in here.
