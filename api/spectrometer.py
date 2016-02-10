import serial
import sys
from time import sleep


ser = serial.Serial('/dev/ttyACM0', 115200)

def wait_for_ready():
    print('-----------before---------')
    data = str(ser.readline())
    while 'ready' not in data:
        data = str(ser.readline())
        sleep(.1)
    print('-- arduino is ready now--')

def do_the_call():
    if len(sys.argv) > 1:
        command_number = int(sys.argv[1])
    else:
        command_number = 3

    received_bytes_string = "b'"+str(command_number)+"\\r\\n'"
    command_in_bytes = bytes(str(command_number), 'ascii')
    print('-----------during call-----------')
    command_didnt_take = True
    while command_didnt_take:
        print('-----calling-----')
        ser.write(command_in_bytes)
        data = str(ser.readline())
        print(data)
        if (data == received_bytes_string):
            print('command was received')
            command_didnt_take = False
        else:
            print('command didnt take: '+data)
        sleep(1)

def get_results():
    print('-----------waiting for results -----------')
    data = str(ser.readline())
    print(data)
    while 'done' not in data:
        data = str(ser.readline())
        print(data)
        sleep(.3)
    print('-- results have been collected --')

do_the_call()
get_results()

