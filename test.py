
import serial   
import os, time
 
# Enable Serial Communication
port = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
 
# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key


port.write('AT'+'\r\n')
port.write('AT+CMGF=1'+'\r\n')
rcv = port.read(100)
print rcv


port.write('AT'+'\r\n')
port.write('AT+COPS=?'+'\r\n')
rcv = port.read(100)
print rcv

port.write('AT+CSQ'+'\r\n')
rcv = port.read(100)
print rcv

port.write('AT+CMGL="REC UNREAD"'+'\r\n')
rcv = port.read(100)
print rcv

port.write('AT+CMGR=1'+'\r\n')
time.sleep(1)
rcv = port.read(256)
print rcv