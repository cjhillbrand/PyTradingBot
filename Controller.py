from MiddleWare import MiddleWare
from Model import Model
from BuyStrategies.BuyUtil import valid_bt, new_buy_strategy
from SellStrategies.SellUtil import valid_st, new_sell_strategy
import math
import time
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

    def fill_data(self, symbol, crypto=False):
        df = self.mw.get_alpha_vantage_symbol(symbol, crypto)

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

    # TODO Change the name iter
    def _set_buy_strategy_iter(self, bt):
        result = dict()
        stock_data = self.model.get_long_stock_data()

        manager = Manager()
        result = manager.dict()
        job = [Process(target=self._parallel_helper, args=(result, stock_data, sym, bt))
               for sym in stock_data.keys()]
        _ = [p.start() for p in job]
        _ = [p.join() for p in job]

        self.model.set_buy_strategy(bt)
        self.model.set_buy_strategy_data(result)
        return self.SUCCESS_CODE

    def _set_sell_strategy_iter(self, st):
        result = dict()
        stock_data = self.model.get_long_stock_data()

        manager = Manager()
        result = manager.dict()
        job = [Process(target=self._parallel_helper, args=(result, stock_data, sym, st))
               for sym in stock_data.keys()]
        _ = [p.start() for p in job]
        _ = [p.join() for p in job]

        self.model.set_sell_strategy(st)
        self.model.set_sell_strategy_data(result)
        return self.SUCCESS_CODE

    def set_buy_strategy(self, bt):
        if type(bt) != int:
            return self._set_buy_strategy_iter(bt)

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
            job = [Process(target=self._parallel_helper, args=(result, stock_data, sym, bt))
                   for sym in stock_data.keys()]
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
        if type(st) != int:
            return self._set_sell_strategy_iter(st)
        if not valid_st(st):
            return self.ERROR_CODE

        st = new_sell_strategy(st)

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

    def simulate_strategies(self, days, verbosity=1):
        if verbosity > 0:
            print("Simulating Strategies")

        # store all of the percent gain for the buy sell strats
        result = dict()

        # Get prices from the Model and crop
        prices_all = self.model.get_long_stock_data()

        bt = self.model.get_buy_strategy()
        st = self.model.get_sell_strategy()

        bt_data_all = self.model.get_buy_strategy_data()
        st_data_all = self.model.get_sell_strategy_data()

        net_worth = 0

        for sym in bt_data_all.keys():
            prices = prices_all[sym]

            if days >= len(prices) or days == -1:
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
                if verbosity > 0:
                    print('No good time to buy %s skipping...' % sym)
                net_worth += CASH_CONSTANT
                result[sym] = -101
                continue
            if verbosity > 1:
                print(bt_times)
                print(st_times)
            CASH_CONSTANT = 20000
            cash = CASH_CONSTANT  # 100,000
            stock_qty = math.floor(cash / prices[bt_times[0]])
            if verbosity > 0:
                print("Initial buy at %f , Qty: %d" % (prices[bt_times[0]], stock_qty))
            cash -= stock_qty * prices[bt_times[0]]
            bt_idx = 1
            if len(st_times) == 0:
                if verbosity > 0:
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
                    bt_idx += 1

                else:
                    cash += prices[st_times[st_idx]] * stock_qty
                    stock_qty = 0
                    st_idx += 1
            if st_idx < len(st_times):
                cash += prices[st_times[-1]] * stock_qty
                stock_qty = 0
            end_stock_val = cash + prices[len(prices) - 1] * stock_qty
            if verbosity > 0:
                print('Percent Gain for %s is: %f%%' % (sym,  (end_stock_val - CASH_CONSTANT) / 2))
            net_worth += end_stock_val
            result[sym] = (end_stock_val - CASH_CONSTANT) / 2

        start_cash = len(prices_all) * CASH_CONSTANT
        if verbosity > -1:
            print('Starting Cash: %d End Cash: %f' % (start_cash, net_worth))
        pct_chg = 100 * (net_worth - start_cash) / start_cash
        if verbosity > -1:
            print('Percent Gain: %f' % pct_chg)
        return result

    def run(self):
        print("Getting real time data is only supported with the crypto symbols"
              "this is supported with the coinbase API")
        # TODO: Grab the stored historical data
        day_data = pd.DataFrame(columns=['Price', 'Time'])
        buy_data = self.model.get_buy_strategy_data()
        sell_data = self.model.get_sell_strategy_data()
        bt = self.model.get_buy_strategy()
        st = self.model.get_sell_strategy()

        # TODO: Create a loop that pulls data from coinbase and appends that data to
        #   the historical data.
        while(True):
            for sym in buy_data.keys():
                curr_price = self.mw.get_crypto_price("spot", sym)
                day_data = day_data.append(curr_price, ignore_index=True)
                # TODO: Once appeneded we need to ask the buy and sell strategies whether or not it is
                #   a good time to buy or sell.
                buy = bt.buy_now(buy_data[sym], day_data)
                sell = st.sell_now(sell_data[sym], day_data)
                price = day_data.tail(1)
                price = price['Price'].values[0]
                if buy:
                    print("Executing buy at: %s" % price)
                if sell:
                    print("Executing sell at: %s" % price)
            time.sleep(60)




        # TODO: If it is a good time to buy or sell, ask coinbase to execute trade

        # TODO: Retrieve info from trade and then send messages via twilio.
