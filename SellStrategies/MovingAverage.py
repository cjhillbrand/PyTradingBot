from SellStrategies.SellStrategy import SellStrategy
import numpy as np


class MovingAverage(SellStrategy):
    SHORT_KEY = 'sk'
    LONG_KEY = 'lk'

    def __init__(self):
        print("\nYou have chosen: Moving Average for a sell strategy")
        self.short_avg = self.__get_avg__("Short Average")
        self.long_avg = self.__get_avg__("Long Average")

    def __get_avg__(self, name):
        val = -1
        while val == -1:
            var_str = input('Please input the %s ( days ):\n--> ' % name)
            try:
                val = int(var_str)
            except ValueError:
                print('"%s" cannot be converted to an int' % var_str)
        return val

    def __calc_avg__(self, avg, data):
        result = np.cumsum(data)
        result[avg:] = result.loc[avg:].reset_index(drop=True) - result.iloc[:-avg].reset_index(drop=True)
        result.loc[:avg] = result.loc[avg]
        return result / avg

    def calc_data(self, df):
        result = dict()
        result[self.SHORT_KEY] = self.__calc_avg__(self.short_avg, df)
        result[self.LONG_KEY] = self.__calc_avg__(self.long_avg, df)
        return result

    def get_sell_times(self, days, data):
        result = list()

        short_data = data[self.SHORT_KEY]
        long_data = data[self.LONG_KEY]

        short_data = short_data[len(short_data) - days:].reset_index(drop=True)
        long_data = long_data[len(long_data) - days:].reset_index(drop=True)

        for i in range(1, len(short_data)):
            try:
                if short_data[i - 1] > long_data[i - 1] and short_data[i] <= long_data[i]:
                    result.append(i)
            except IndexError as ix:
                print('Encountered Index error find sell times at index %d' % i)
        return result




