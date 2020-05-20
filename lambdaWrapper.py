import boto3
import os
import json

class MailLambda:
    def __init__(self):
        self.client = boto3.client('lambda')
        self.LAMBDA_ARN = "arn:aws:lambda:eu-west-1:357832308593:function:sms_to_email"
        
    def send(self, payload):
        try: 
            print(json.dumps(payload))
            response = self.client.invoke(
                FunctionName=self.LAMBDA_ARN,
                Payload=json.dumps(payload),
                InvocationType='Event'
            )
        except Exception as e:
            print("invoke failed: {}".format(e))

