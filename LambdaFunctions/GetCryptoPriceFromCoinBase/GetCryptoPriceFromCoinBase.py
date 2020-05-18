import boto3
from coinbase.wallet import client as cl

client = boto3.client('ssm');
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):

    # Grab all of the parameters from SSM
    name = client.get_parameter(Name='/CryptoName')
    cbkey = client.get_parameter(Name='/Coinbase/key') # To Do add to Parameter store
    cbsecret = client.get_parameter(Name='/Coinbase/secret') # To Do add to parameter store
    
    name = name['Parameter']['Value']
    cbkey = cbkey['Parameter']['Value']
    cbsecret = cbsecret['Parameter']['Value']

    
    # Query the database for the Coinbase values 
    cb_client = cl.Client(cbkey, cbsecret)    
    price = cb_client.get_spot_price(currency_pair=name + '-USD')


    db_value = price['amount']

    lambda_client.invoke(
        FunctionName='StorePriceInDB',
        InvocationType='Event',
        LogType='None',
        Payload='' + db_value
        )
    return {'statusCode': 200, 'Value': db_value}    

