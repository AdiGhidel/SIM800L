from time import sleep
from sim800l import SIM800L
from lambdaWrapper import MailLambda
import datetime

sim800l=SIM800L('/dev/ttyS0')
client = MailLambda()

LAMBDA_ARN = "arn:aws:lambda:eu-west-1:357832308593:function:sms_to_email"

while True:
    print("reading:{}".format(datetime.datetime.now()))
    sms  = sim800l.read_sms() 
    for s in sms:
        if s:
            client.send(s)