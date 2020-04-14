import json
import pandas as pd
from datetime import datetime as dt
import time
from tzlocal import get_localzone
import urllib.request, urllib.error
from twilio.rest import Client
from coinbase.wallet import client
import os


class MiddleWare:
    ALPHA_VANTAGE_TO = 'Thank you for using Alpha Vantage! Our standard API call ' \
                       'frequency is 5 calls per minute and 500 calls per day. Please visit ' \
                       'https://www.alphavantage.co/premium/ if you would like to target a ' \
                       'higher API call frequency.'
    ALPHA_VANTAGE_ERR = 'Error Message'
    ALPHA_VANTAGE_NOTE = 'Note'
    RET_ERR_CODE = -1
    RET_MARK_CLOSE = -2
    OPENING_HOUR = 14
    OPENING_MIN = 30
    CLOSING_HOUR = 21

    def __init__(self):
        with open('./AlphaVantageApiKey.json') as fid:
            data = json.load(fid)
            self.key = data['Key']
            twilio_sid = data['account_sid']
            twilio_auth = data['auth_token']
            self.t_client = Client(twilio_sid, twilio_auth)
            self.numbers = data['numbers']
            self.from_number = data['phone_number']
            cbkey = data['Coinbase']['key']
            cbsecret = data['Coinbase']['secret']
            self.cbClient = client.Client(cbkey, cbsecret)
            self.tz = get_localzone()
            self.retry = 0

    # TODO create another parameter called 'force' that calls alpha vantage even if
    #   a file is saved locally
    # FIXME With the loading bar there is a weird printing when there is an error.
    def get_alpha_vantage_symbol(self, symbol, crypto=False):
        if self.retry == 5:
            raise Exception('AlphaVantageRetryLimit')
        if (crypto):
            url_string = "https://www.alphavantage.co/query?function=" \
                         "DIGITAL_CURRENCY_DAILY&symbol=%s&market=USD&apikey=%s" % (symbol, self.key)
        else:
            url_string = "https://www.alphavantage.co/query?function=" \
                     "TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s" % (symbol, self.key)

        file = "./data/" + symbol + "_data.csv"
        if not os.path.exists(file):
            try:
                with urllib.request.urlopen(url_string) as url:
                    data = json.loads(url.read().decode())

                    if self.ALPHA_VANTAGE_ERR in data:
                        return self.RET_ERR_CODE

                    if self.ALPHA_VANTAGE_NOTE in data:
                        if data[self.ALPHA_VANTAGE_NOTE] == self.ALPHA_VANTAGE_TO:
                            print('Timeout Exception... Trying in 60 seconds.')
                            print('[', end='')
                            for i in range(1, 60):
                                time.sleep(1)
                                print('#', end='')
                            print(']')
                            self.retry += 1
                            return self.get_alpha_vantage_symbol(symbol)

                    # extract the data
                    if crypto:
                        cols = ['3b. low (USD)', '2a. high (USD)', '4a. close (USD)', '1a. open (USD)']
                        data = data['Time Series (Digital Currency Daily)']
                        df = self._format_json(data, '%Y-%m-%d', cols)
                    else:
                        data = data['Time Series (Daily)']
                        df = self._format_json(data, '%Y-%m-%d')
                    print('Data saved to : %s' % file)
                    df.to_csv(file)

            except urllib.error.HTTPError as err:
                if err.code == 503:
                    print('Service Temporarily Unavailable... Trying in 60 seconds.')
                    print('[', end='')
                    for i in range(1, 60):
                        time.sleep(1)
                        print('#', end='')
                    print(']')
                    self.retry += 1
                    return self.get_alpha_vantage_symbol(symbol)

        # If the data is already there, just load it from the CSV
        else:
            df = pd.read_csv(file)

        df.sort_values(by='Date', ascending=True, inplace=True, ignore_index=True)
        self.retry = 0
        return df

    def get_intraday_symbol(self, symbol):
        url_string = "https://www.alphavantage.co/query?function=" \
                     "TIME_SERIES_INTRADAY&symbol=%s&interval=1min&outputsize=compact&apikey=%s" % (symbol, self.key)
        ts = time.time()
        utc_now = dt.utcfromtimestamp(ts)
        if utc_now.hour < self.OPENING_HOUR or \
                (utc_now.hour == self.OPENING_HOUR and utc_now.minute < self.OPENING_MIN) \
                or utc_now.hour >= self.CLOSING_HOUR:
            # TODO It would be cool to print a count down to when the market opens up.
            print('Market is closed')
            return self.RET_MARK_CLOSE

        # Execute request
        with urllib.request.urlopen(url_string) as url:
            data = json.loads(url.read().decode())

            if self.ALPHA_VANTAGE_ERR in data:
                return self.RET_ERR_CODE

            data = data['Time Series (1min)']
            df = self._format_json(data, '%Y-%m-%d %H:%M:%S')
            print(df.head())

    def _format_json(self, data, time_format, columns=['3. low', '2. high', '4. close', '1. open']):
        df = pd.DataFrame(columns=['Date', 'Low', 'High', 'Close', 'Open'])
        for k, v in data.items():
            date = dt.strptime(k, time_format)  # )
            data_row = [date, float(v[columns[0]]), float(v[columns[1]]),
                        float(v[columns[2]]), float(v[columns[3]])]
            df.loc[-1, :] = data_row
            df.index = df.index + 1
        return df

    def send_twilio_msg(self, message):
        for n in self.numbers:
            message = self.t_client.messages \
                .create(
                    body=message,
                    from_=self.from_number,
                    to=n
                )

    def get_crypto_price(self, type_price, symbol):
        if type_price == "buy":
            price = self.cbClient.get_buy_price(currency_pair=symbol + '-USD')
        elif type_price == "sell":
            price = self.cbClient.get_sell_price(currency_pair=symbol + '-USD')
        else:
            price = self.cbClient.get_spot_price(currency_pair=symbol + '-USD')
        ts = time.time()
        utc_now = dt.utcfromtimestamp(ts)
        return {'Price': price['amount'], 'Time': utc_now}

    def execute_trade(self, trade_type):
        if trade_type == 'buy':
            print("Buying")
        elif trade_type == 'sell':
            print("selling")
