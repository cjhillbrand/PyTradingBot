import psycopg2
from MiddleWare import MiddleWare

hostname = 'localhost'
username = 'cj'
password = 'Legomann23'
database = 'TradingBot'
myConnection = psycopg2.connect(host=hostname, user=username, password=password,
                                dbname=database)
mw = MiddleWare()
cur = myConnection.cursor()
while (True):
    price = mw.get_crypto_price("spot", 'BTC')
    cur.execute("INSERT INTO dailycryptodata (symbol, datetime, price) VALUES ('BTC', CURRENT_TIMESTAMP, " +
                price['Price'] + ")")
    myConnection.commit()

myConnection.close()
