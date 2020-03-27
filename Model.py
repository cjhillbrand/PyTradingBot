class Model:
    def set_long_stock_data(self, df):
        self.long_stock_data = df

    def get_long_stock_data(self):
        if hasattr(self, "long_stock_data"):
            return self.long_stock_data

    def set_all_data(self, df):
        self.all_data = df

    def get_all_data(self):
        if hasattr(self, "all_data"):
            return self.all_data

    def set_buy_strategy(self, bt):
        self.buy_strategy = bt

    def get_buy_strategy(self):
        if hasattr(self, "buy_strategy"):
            return self.buy_strategy

    def set_buy_strategy_data(self, bt_data):
        self.buy_strategy_data = bt_data

    def get_buy_strategy_data(self):
        if hasattr(self, "buy_strategy_data"):
            return self.buy_strategy_data

    def set_sell_strategy(self, st):
        self.sell_strategy = st

    def get_sell_strategy(self):
        if hasattr(self, "sell_strategy"):
            return self.sell_strategy

    def set_sell_strategy_data(self, st_data):
        self.sell_strategy_data = st_data

    def get_sell_strategy_data(self):
        if hasattr(self, "sell_strategy_data"):
            return self.sell_strategy_data
