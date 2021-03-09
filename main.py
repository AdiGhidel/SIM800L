from time import sleep
from sim800l import SIM800L
from lambdaWrapper import MailLambda

import datetime
import argparse
import logging

from argparse import ArgumentParser


# Variables
LAMBDA_ARN = "arn:aws:lambda:eu-west-1:357832308593:function:sms_to_email"


def set_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--log-level",
        default=logging.INFO,
        type=lambda x: getattr(logging, x),
        help="Configure the logging level."
    )
    parser.add_argument(
        "--dry-run",
        default=True,
        help="Stops emails form being sent / message deletes"
    )
    args=parser.parse_args()
    return args

def set_logger(args):
    logger = logging.getLogger("sms-main")
    logging.basicConfig(level = args.log_level)
    return logger
    
def main():
    # Set-up
    args = set_parser()
    logger = set_logger(args)
    sim800l=SIM800L('/dev/ttyS0', logger)
    client=MailLambda() 
    

    while True:
        print("reading:{}".format(datetime.datetime.now()))
        sms=sim800l.read_sms()
        sleep(1)
        for s in sms:
            if s:
                sim800l.write_to_file(s)
                client.send(s)

if __name__ == "__main__":
    main()
