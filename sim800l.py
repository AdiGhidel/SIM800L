
import os
import time
import sys
import serial
import datetime
import io
from binascii import unhexlify
import string


def convert_to_string(buf):
    try:
        tt = buf.decode('utf-8').strip()
        return tt
    except UnicodeError:
        tmp = bytearray(buf)
        for i in range(len(tmp)):
            if tmp[i] > 127:
                tmp[i] = ord('#')
        return bytes(tmp).decode('utf-8').strip()


def fix_utf16(buf):
    if all(c in string.hexdigits for c in buf):
        try:
            tt = unhexlify(buf).decode("utf-16-be")
            return tt
        except:
            print("not utf16-be")
    return buf


class SIM800L:
    def __init__(self, ser, logger):
        try:
            self.ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
            self.logger = logger
        except Exception as e:
            sys.exit("Error: {}".format(e))

    def set_msg(self):
        self.logger.debug(">set_msg")
        self.ser.write('AT+CMGF=1\r\n'.encode())
      

    def update_payloads(self, payloads, sender, msg, date):
        self.logger.debug(">Update_payloads")

        date = self.get_date(date)

        if len(payloads) > 0:
            self.logger.info("Payload not empty")
            found = False
            for p in payloads:
                if p.exists(sender, date):
                    p.update(msg)
                    found = True
                    self.logger.info("Found existing message")
                    break
            if not found:
                self.logger.info("Created new entry")
                payloads.append(Payload(sender, date, msg))
        else:
            payloads.append(Payload(sender, date, msg))

    def skip_line(self, line):
        self.logger.debug(">Update_payloads")
        skip = not line or "AT+CM" in line or "OK" in line
        self.logger.debug("skip line {}: {}".format(line, skip))
        return skip        

    def read_sms(self):
        self.logger.debug(">Read_sms")
        # vars
        payloads = []

        # skip whatever was left
        while self.ser.in_waiting:
            self.logger.debug("old messages on serial")
            self.ser.readline()

        self.set_msg()

        for i in range(1, 6):
            self.logger.debug("iteration {}".format(i))
            time.sleep(0.5)
            cmd = 'AT+CMGR={}\n'.format(i)
            # write async_command
            self.ser.write(cmd.encode())
            b = []

            for _ in range(7):
                x = self.ser.readline()
                self.logger.debug("Read line raw:{}".format(x))
                line = convert_to_string(x)
                self.logger.debug("Read line string:{}".format(line))
                if self.skip_line(line):
                    continue

                b.append(line)
            sender, date, msg = self.parse_buf(b)
            
            msg_fix = fix_utf16(msg)
            self.logger.debug("Fixed message from: <<<{}>>>  to <<<{}>>>".format(msg, msg_fix))

            if sender and date:
                self.logger.info("Valid message")
                time.sleep(1)
                self.delete_sms(i)
                self.update_payloads(payloads, sender, msg_fix, date)

        return [p.to_mail() for p in payloads]

    def parse_buf(self, buf):
        self.logger.debug(">Parse_buf")
        sender = ""
        date = ""
        msg = ""
        for el in buf:
            if "+CMGR" in el:
                el_split = el.split(",")
                if len(el_split) == 5:
                    sender = el_split[1]
                    date = el_split[3] + "/" + el_split[4]
            else:
                msg += el
        self.logger.debug("Sender: {}, date: {}, msg: {}".format(sender, date, msg))
        return (sender, date, msg)

    def delete_sms(self, id):
        self.logger.debug(">delete_sms")
        self.logger.info("deleting {}".format(id))
        self.async_command('AT+CMGD={}\n'.format(id), 1)

    def get_date(self, date):
        self.logger.debug(">get_date")
        date_obj = datetime.datetime.strptime(date, '"%y/%m/%d/%H:%M:%S+%f"')
        return date_obj

    def delete_all(self):
        self.logger.debug(">delete_all")
        self.logger.info("deleting all messages")
        self.async_command('AT+CMGDA="DEL ALL"\n', 1)

    def async_command(self, cmdstr, lines=1):
        self.logger.debug(">async_command")
        self.logger.debug("command: {}".format(cmdstr))
        # Read what was left rest
        while self.ser.in_waiting:
            self.ser.readline()
        self.ser.write(cmdstr.encode())
        time.sleep(0.7)

    def write_to_file(self, message):
        self.logger.debug(">write_to_file")
        # read existing
        f = open("/home/pi/messages.txt", "r")
        content = f.read()
        self.logger.info("Content: {}".format(content))
        f.close()
        message_idx = 1
        number=content.split("===")
        if len(number) > 2:
            message_idx = int(number[-2]) + 1
 
        # write to file
        f = open("/home/pi/messages.txt", "a")
        f.write("==={}===\n".format(message_idx))
        f.write(message["SMS"])
        f.write("\n")
        f.close()

class Payload:
    def __init__(self, sender, date, msg):
        self.sender = sender
        self.date = date
        self.msg = msg

    def exists(self, sender, date):
        if self.sender == sender:
            if abs(self.date - date) < datetime.timedelta(seconds=60):
                return True
        return False

    def update(self, message):
        self.msg += "<##>" + message

    def to_mail(self):
        return {"SMS": 'From: {}\nDate: {}\n{}'.format(self.sender, self.date.strftime("%d/%m/%y %H:%M"), self.msg)}
