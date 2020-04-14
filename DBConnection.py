import psycopg2

hostname = 'localhost'
username = 'cj'
password = 'Legomann23'
database = 'TradingBot'
myConnection = psycopg2.connect(host=hostname, user=username, password=password,
                                dbname=database)
cur = myConnection.cursor()

cur.execute("INSERT INTO historicaldata (symbol, open_price) VALUES ('TSTE', '10.0')")

myConnection.commit()

myConnection.close()
