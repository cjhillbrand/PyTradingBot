from MiddleWare import MiddleWare
from Model import Model
from BuyStrategies.BuyUtil import valid_bt, new_buy_strategy
from SellStrategies.SellUtil import valid_st, new_sell_strategy
import math
import pandas as pd
import progressbar
from multiprocessing import Process, Manager

class Controller:

    ERROR_CODE = -1
    SUCCESS_CODE = 1
    CEIL_PRICE = 40
    FLOOR_PRICE = 5
    SAMPLES = 500
    RANDOM_STATE = 42

    def __init__(self, model):
        self.mw = MiddleWare()
        self.model = model

    def fill_data(self, symbol):
        df = self.mw.get_alpha_vantage_symbol(symbol)

        # This is our error check since across the program
        # we use the Error code -1 to signify a fault
        if type(df) == int:
            return self.ERROR_CODE

        # Store the df in the model
        result_all = dict()
        result_prices = dict()
        result_all[symbol] = df
        result_prices[symbol] = df['Close']
        self.model.set_long_stock_data(result_prices)
        self.model.set_all_data(result_all)

        return self.SUCCESS_CODE

    def load_russell(self):
        df = pd.read_csv('./data/russell_2000.csv')
        of_interest = df[(df['Price'] <= self.CEIL_PRICE) & (df['Price'] > self.FLOOR_PRICE)]
        of_interest = of_interest.sample(n=self.SAMPLES, random_state=self.RANDOM_STATE)
        result_all = dict()
        result_prices = dict()
        unable_to_load = 0
        bar = progressbar.ProgressBar(maxval=len(of_interest),
                                      widgets=[progressbar.Bar('=', '[', ']'), progressbar.Percentage()])
        bar.start()
        i = 0
        bad_sym = list()
        for sym in of_interest['Ticker']:
            i += 1
            ticker_data = self.mw.get_alpha_vantage_symbol(sym)

            if type(ticker_data) == int:
                unable_to_load += 1
                bad_sym.append(sym)
                continue

            result_all[sym] = ticker_data
            result_prices[sym] = ticker_data['Close']
            bar.update(i)
        bar.finish()

        # store data in Model
        print('Unable to load %d symbol(s): %s' % (unable_to_load, ' '.join(bad_sym)))
        self.model.set_long_stock_data(result_prices)
        self.model.set_all_data(result_all)

        return self.SUCCESS_CODE

    def _parallel_helper(self, result, stock_data, sym, t):
        result[sym] = t.calc_data(stock_data[sym])

    def set_buy_strategy(self, bt):
        if not valid_bt(bt):
            return self.ERROR_CODE

        # Construct a new buy strategy according to the BuyType that we
        # have been passed.
        bt = new_buy_strategy(bt)

        # Calculate the data that we need for the buy strategy. This changes depending
        # on the buy strategy, but it returns a dictionary regardless.
        stock_data = self.model.get_long_stock_data()

        # Parallel Computation
        if len(stock_data) > 100:
            manager = Manager()
            result = manager.dict()
            job = [Process(target=self._parallel_helper, args=(result, stock_data, sym, bt)) for sym in stock_data.keys()]
            _ = [p.start() for p in job]
            _ = [p.join() for p in job]
        # Iterative computation
        else:
            result = dict()
            bar = progressbar.ProgressBar(maxval=len(stock_data.keys()),
                                          widgets=[progressbar.Bar('=', '[', ']'), progressbar.Percentage()])
            bar.start()
            i = 0
            for sym in stock_data.keys():
                buy_strategy_data = bt.calc_data(stock_data[sym])
                result[sym] = buy_strategy_data
                i += 1
                bar.update(i)
            bar.finish()

        self.model.set_buy_strategy(bt)
        self.model.set_buy_strategy_data(result)

        return self.SUCCESS_CODE

    def set_sell_strategy(self, st):
        if not valid_st(st):
            return self.ERROR_CODE

        st = new_sell_strategy(st)
        result = dict()

        # Calculate the data that we need for the sell strategy. This changes depending
        # on the sell strategy, but it returns a dictionary regardless
        stock_data = self.model.get_long_stock_data()
        if len(stock_data) > 100:
            manager = Manager()
            result = manager.dict()
            job = [Process(target=self._parallel_helper, args=(result, stock_data, sym, st)) for sym in
                   stock_data.keys()]
            _ = [p.start() for p in job]
            _ = [p.join() for p in job]
        else:
            result = dict()
            bar = progressbar.ProgressBar(maxval=len(stock_data.keys()),
                                          widgets=[progressbar.Bar('=', '[', ']'), progressbar.Percentage()])
            bar.start()
            i = 0
            for sym in stock_data.keys():
                sell_strategy_data = st.calc_data(stock_data[sym])
                result[sym] = sell_strategy_data
                i += 1
                bar.update(i)

        self.model.set_sell_strategy(st)
        self.model.set_sell_strategy_data(result)

        return self.SUCCESS_CODE

    def simulate_strategies(self, days):
        print("Simulating Strategies")

        # Get prices from the Model and crop
        prices_all = self.model.get_long_stock_data()

        bt = self.model.get_buy_strategy()
        st = self.model.get_sell_strategy()

        bt_data_all = self.model.get_buy_strategy_data()
        st_data_all = self.model.get_sell_strategy_data()

        net_worth = 0

        for sym in bt_data_all.keys():
            prices = prices_all[sym]

            if days >= len(prices):
                days = len(prices) - 1

            if days < 0:
                return self.ERROR_CODE

            # This manipulation is done in place. I checked and it doesn't alter
            # the underlying Model, which is good, but if it does this is where to look.
            prices = prices.tail(n=days)
            prices.reset_index(inplace=True, drop=True)

            bt_data = bt_data_all[sym]
            st_data = st_data_all[sym]

            bt_times = bt.get_buy_times(days, bt_data)
            st_times = st.get_sell_times(days, st_data)

            if len(bt_times) == 0:
                print('No good time to buy %s skipping...' % sym)
                net_worth += 2000
                continue

            cash = 2000  # 100,000
            stock_qty = math.floor(cash / prices[bt_times[0]])
            print("Initial buy at %f , Qty: %d" % (prices[bt_times[0]], stock_qty))
            cash -= stock_qty * prices[bt_times[0]]
            bt_idx = 1
            if len(st_times) == 0:
                print('No good time to sell %s selling on last day...' % sym)
                st_idx = 0
            elif st_times[len(st_times) - 1] < bt_times[0]:
                st_idx = len(st_times)
            else:
                st_idx = st_times.index(next(x for x in st_times if x > bt_times[0]))  # Grab the first sell index thats after

            while bt_idx < len(bt_times) and st_idx < len(st_times):
                if bt_times[bt_idx] < st_times[st_idx]:
                    # TODO figure out an approppiate number of stocks to sell and buy
                    stock_qty = math.floor(cash / prices[bt_times[bt_idx]])
                    cash -= stock_qty * prices[bt_times[bt_idx]]
                    # print("Buying all stonks at %f on day %d \nTotal Cash on hand: %f"
                    #      % (prices[bt_times[bt_idx]], bt_times[bt_idx], cash))
                    bt_idx += 1

                else:
                    cash += prices[st_times[st_idx]] * stock_qty
                    stock_qty = 0
                    # print("Selling all stonks at %f on day %d \nTotal Cash on hand: %f"
                    #      % (prices[st_times[st_idx]], st_times[st_idx], cash))
                    st_idx += 1
            if st_idx < len(st_times):
                cash += prices[st_times[-1]] * stock_qty
                stock_qty = 0
            end_stock_val = cash + prices[len(prices) - 1] * stock_qty
            print('Percent Gain for %s is: %f%%' % (sym,  (end_stock_val - 2000) / 20))
            net_worth += end_stock_val

        start_cash = len(prices_all) * 2000
        print('Starting Cash: %d End Cash: %f' % (start_cash, net_worth))
        pct_chg = 100 * (net_worth - start_cash) / start_cash
        print('Percent Gain: %f' % pct_chg)
        return self.SUCCESS_CODE

    def run(self):
        print('Trading Bot is running')
