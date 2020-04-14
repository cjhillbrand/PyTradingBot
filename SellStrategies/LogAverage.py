import math

from SellStrategies.SellStrategy import SellStrategy
import numpy as np


class LogAverage(SellStrategy):
    SHORT_KEY = 'sk'
    LONG_KEY = 'lk'

    def __init__(self, long=-1):
        if long == -1:
            print("\nYou have chosen: Log based Average for a sell strategy")
            while long == -1:
                var_str = input('Please input the Long Average ( days ):\n--> ')
                try:
                    long = int(var_str)
                except ValueError:
                    print('"%s" cannot be converted to an int' % var_str)
        self.long = long

    def calc_data(self, df):
        if self.long >= len(df):
            self.long = len(df) - 1
        result = dict()
        temp = np.log(df)
        result[self.SHORT_KEY] = temp
        temp = np.cumsum(temp)
        temp[self.long:] = temp.loc[self.long:].reset_index(drop=True) - temp.iloc[:-self.long].reset_index(drop=True)
        temp.loc[:self.long] = temp.loc[self.long]
        result[self.LONG_KEY] = temp / self.long
        return result

    def get_sell_times(self, days, data):
        result = list()

        short_data = data[self.SHORT_KEY]
        long_data = data[self.LONG_KEY]

        # The data is stored so that index 0 is the first day.
        # This grabs the earliest day and then the latest day
        short_data = short_data[len(short_data) - days:].reset_index(drop=True)
        long_data = long_data[len(long_data) - days:].reset_index(drop=True)

        for i in range(1, len(short_data)):
            try:
                if short_data[i - 1] < long_data[i - 1] and short_data[i] >= long_data[i]:
                    result.append(i)
            except IndexError as ix:
                print('Encountered Index error solving buy times at: %d' % i)
                exit(1)
        return result

    def sell_now(self, historical_data, data):
        curr_price = data.tail(1)
        curr_price = curr_price['Price'].values[0]

        historical_data = historical_data[self.LONG_KEY]
        return historical_data.tail(1).values[0] > math.log(float(curr_price))
