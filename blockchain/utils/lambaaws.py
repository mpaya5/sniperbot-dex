import boto3
s3 = boto3.resource('s3', region_name='ap-southeast-2')
import json
import os
import base64

from eth_account.datastructures import SignedTransaction

from dotenv import load_dotenv
load_dotenv()

class LambdaSigner:
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
        self.function_name = os.getenv('AWS_LAMBDA_FUNCTION_NAME')

    def sign_transaction(self, transaction_data):
        #Añadir la clave privada al objeto transaction_data
        transaction_data['privateKey'] = os.getenv('SKEYS')
        response = self.lambda_client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(transaction_data),
        )

        response_payload = json.load(response['Payload'])
        signed_tx = SignedTransaction(
            rawTransaction=response_payload['signed_tx']['rawTransaction'],
            hash=response_payload['signed_tx']['hash'],
            r=int(response_payload['signed_tx']['r']),
            s=int(response_payload['signed_tx']['s']),
            v=response_payload['signed_tx']['v']
        )

        return signed_tx

