
import serial   
import os, time
 
# Enable Serial Communication
port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=2)
 
# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key

def command(val):
    port.write(val+'\r\n')
    rcv = port.read(128)
    print rcv

command("AT")

command('AT+CBAND?')

# command('AT+COPS=?')

command('AT+CSQ')

command("AT+CREG?")

command('AT+CMGL="ALL"')

command('AT+CMGR=1')

command('AT+CMGF=1')

# command("AT+CNMI=1,2,0,0,0")

while(True):
    print(port.read())


