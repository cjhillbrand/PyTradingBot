import psycopg2
import os
import json

db_hostname = os.environ['db_hostname']
db_database = os.environ['db_database']
db_username = os.environ['db_username']
db_password = os.environ['db_password']

conn = psycopg2.connect("dbname='%s' user='%s' host='%s' port='5432' password='%s'" % (db_database, db_username, db_hostname, db_password))


def lambda_handler(event, context):
    name = os.environ['cryptoname']

    # insert into Database
    cursor = conn.cursor()

    cursor.execute("INSERT INTO dailycryptodata (symbol, datetime, price) VALUES ('%s', CURRENT_TIMESTAMP, %s)" % (name, event))
    
    # Commit Transaction
    conn.commit()


    return {
        'statusCode': 200,
    }

