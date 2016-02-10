import serial
import sys
from time import sleep


class Spectrometer(object):

    def __init__(self, console_output=False):
        self.ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
        self.console_output = console_output

    def take_spectrometer_reading(self):
        self.do_the_call(1)
        return self.get_results()

    def take_fluorescence_reading(self):
        self.do_the_call(2)
        return self.get_results()

    def take_color_reading(self):
        self.do_the_call(3)
        return self.get_results()

    def do_the_call(self, command_number):
        self.ser.reset_input_buffer()
        received_bytes_string = "b'"+str(command_number)+"\\r\\n'"
        command_in_bytes = bytes(str(command_number), 'ascii')
        if self.console_output: print('-----------during call-----------')
        command_didnt_take = True
        while command_didnt_take:
            if self.console_output: print('-----calling-----')
            self.ser.write(command_in_bytes)
            data = str(self.ser.readline())
            if self.console_output: print(data)
            if (data == received_bytes_string):
                if self.console_output: print('command was received')
                command_didnt_take = False
            else:
                if self.console_output: print('command didnt take: '+data)
            sleep(1)

    def get_results(self):
        data = []
        if self.console_output: print('-----------waiting for results -----------')
        data.append(str(self.ser.readline()))
        if self.console_output: print(data[-1])
        while 'done' not in data[-1]:
            data.append(str(self.ser.readline()))
            if self.console_output: print(data[-1])
            sleep(.3)
        if self.console_output: print('-- results have been collected --')
        the_string_of_data = data[-2][2:-1]  # truncate 'b' at the front of the string
        data_as_array = the_string_of_data.split(',')[:-1] # truncate junk data with newline after the last comma
        if len(data_as_array) == 256:
            return data_as_array
        else:
            return False


if __name__ == '__main__':
    spectrometer = Spectrometer(console_output=True)
    if len(sys.argv) > 1:
        command_number = int(sys.argv[1])
    else:
        command_number = 3
    spectrometer.do_the_call(command_number)
    spectrometer.get_results()
