class SellStrategy:

    # Prompts the user for any info that it may need.
    def __init__(self):
        raise Exception("SUBCLASS MUST IMPLEMENT CONSTRUCTOR")

    # Takes in the long stock data and returns a dictionary
    # where each key is a seperate analysis on the whole stock data
    def calc_data(self, df):
        raise Exception("SUBCLASS MUST IMPLEMENT _CALC_DATA")

    def get_sell_times(self, days, data):
        raise Exception("SUBCLASS MUST IMPLEMENT GET_BUY_TIME")