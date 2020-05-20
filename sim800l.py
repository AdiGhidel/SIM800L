
import os,time,sys
import serial
import datetime
from binascii import unhexlify
import string

def convert_to_string(buf):
    try:
        tt = buf.decode('utf-8').strip()
        return tt
    except UnicodeError:
        tmp = bytearray(buf)
        for i in range(len(tmp)):
            if tmp[i]>127:
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
    def __init__(self,ser):
        try:
            self.ser=serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
        except Exception as e:
            sys.exit("Error: {}".format(e))

    def read_sms(self):
        # skip whatever was left
        while self.ser.in_waiting:
            self.ser.readline()

        self.set_msg()
        payloads = []
        for i in range(1,10):
            cmd = 'AT+CMGR={}\n'.format(i)
            #write command
            self.ser.write(cmd.encode())
            b = []
            for j in range(6):
                x = self.ser.readline()
                # print(x)
                line = convert_to_string(x)
                if "AT+CM" in line:
                    continue
                if "OK" in line:
                    continue
                if not line:
                    continue
                b.append(line)
            sender, date, msg = self.parse_buf(b)
            msg = fix_utf16(msg)
            if sender and date:
                date = self.get_date(date)
                time.sleep(1)
                self.delete_sms(i)
                if len(payloads) > 0:
                    found = False
                    for p in payloads:
                        if p.exists(sender, date):
                            p.update(msg)
                            found = True
                            break
                    if not found:
                        payloads.append(Payload(sender, date, msg))  
                else: 
                    payloads.append(Payload(sender, date, msg))
        return [p.to_mail() for p in payloads]

    def parse_buf(self, buf):
        sender = ""
        date = ""
        msg = ""
        for el in buf:
            if "+CMGR" in el:
                el_split = el.split(",")
                if len(el_split) == 5:
                    sender = el_split[1]    
                    date = el_split[3] + "/"+ el_split[4]
            else:
                msg += el
        return (sender, date, msg)

    def delete_sms(self,id):
        print("deleting {}".format(id))
        self.command('AT+CMGD={}\n'.format(id),1)

    def check_incoming(self): 
        if self.ser.in_waiting:
            buf=self.ser.readline()
            print(buf)
            buf = convert_to_string(buf)
            params=buf.split(',')

            if params[0][0:5] == "+CMTI":
                self._msgid = int(params[1])
                if self.msg_action:
                    self.msg_action()

            elif params[0] == "NO CARRIER":
                    self.no_carrier_action()

            elif params[0] == "RING" or params[0][0:5] == "+CLIP":
                #@todo handle
                pass

    def get_date(self,date):
        date_obj = datetime.datetime.strptime(date, '"%y/%m/%d/%H:%M:%S+%f"')
        return date_obj

    def delete_all(self):
        self.command('AT+CMGDA="DEL ALL"\n',1)

class Payload:
    def __init__(self,sender, date, msg):
        self.sender = sender
        self.date = date
        self.msg = msg
    
    def exists(self, sender, date):
        if self.sender == sender:
            if abs(self.date - date) < datetime.timedelta(seconds=60):
                return True
        return False
    
    def update(self, message):
        self.msg += "<<SPLIT>>" + message

    def to_mail(self):
        return { "SMS": '({}) - {}>>{}'.format(self.sender, self.date, self.msg) }  