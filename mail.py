####
# mail.py 
# lambda code 
####

import json
import boto3
import secrets
from hashlib import sha1

from botocore.exceptions import ClientError


def sms_payload(sms):
    
    BODY_TEXT = (
        "Ai primit urmatorul mesaj: {} ".format(sms))

    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <p>Ai primit urmatorul mesaj:  {}</p>
      <p>Numai bine,</p>
      <p>Raspberry</p>
    </body>
    </html>
    """.format(sms)

    # The character encoding for the email.
    CHARSET = "UTF-8"
    SUBJECT = "[SMS] primit"

    return {
        "SUBJECT": SUBJECT,
        "BODY_TEXT": BODY_TEXT,
        "BODY_HTML": BODY_HTML,
        "CHARSET": CHARSET
    }


def main(event, context):

    client = boto3.client('ses')

    # This address must be verified with Amazon SES.
    SENDER = ""
    RECIPIENT = ""

    # Sanitize the input
    if "SMS" in event:
        sms = event["SMS"]
    else:
        return {
            'statusCode': 400,
            'body': "Missing SMS configuration"
        }
    #Set-up the message
    message = sms_payload(sms)

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': message["CHARSET"],
                        'Data': message["BODY_HTML"],
                    },
                    'Text': {
                        'Charset': message["CHARSET"],
                        'Data': message["BODY_TEXT"],
                    },
                },
                'Subject': {
                    'Charset': message["CHARSET"],
                    'Data': message["SUBJECT"],
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    return {
        'statusCode': 200,
        'body': "sent"
    }
