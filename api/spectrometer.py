import logging
import sys
from time import sleep

import serial

from api.exceptions import SpectrometerSerialError


class Spectrometer(object):
    '''
    Interfaces with the Spectrometer via the serial port
    '''
    def __init__(self):
        self.ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)  # TODO move this to the config file
        self.max_number_of_retries = 3  # TODO move this to the config file
        self.logger = logging.getLogger('spectro')

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
        '''
        Interface with the spectrometer via the serial port
        '''
        self.ser.reset_input_buffer()
        received_bytes_string = "b'" + str(command_number) + "\\r\\n'"
        command_in_bytes = bytes(str(command_number), 'ascii')
        self.logger.info('-----------during call-----------')
        command_didnt_take = True
        num_calls = 0
        while command_didnt_take:
            self.logger.info('-----calling spectrometer-----')
            self.ser.write(command_in_bytes)
            data = str(self.ser.readline())
            self.logger.info('Spectrometer data is ' + data)
            if (data == received_bytes_string):
                self.logger.info('command was received by spectrometer')
                command_didnt_take = False
            else:
                self.logger.warning('command didnt take: ' + data)
            num_calls += 1
            if num_calls > self.max_number_of_retries:
                raise SpectrometerSerialError  # TODO this isn't meshing with rest_framework correctly.  Troubleshoot
            sleep(1)

    def get_results(self):
        data = []
        self.logger.info('-----------waiting for results -----------')
        data.append(str(self.ser.readline()))
        self.logger.info(data[-1])
        while 'done' not in data[-1]:
            data.append(str(self.ser.readline()))
            self.logger.info(data[-1])
            sleep(.3)
        self.logger.info('-- results have been collected --')
        the_string_of_data = data[-2][2:-1]  # truncate 'b' at the front of the string
        data_as_array = the_string_of_data.split(',')[:-1]  # truncate junk data with newline after the last comma
        data_as_int_array = [int(x) for x in data_as_array if x.isdigit()]
        if len(data_as_int_array) == 256:
            return data_as_int_array
        else:
            return []


if __name__ == '__main__':
    spectrometer = Spectrometer()
    if len(sys.argv) > 1:
        command_number = int(sys.argv[1])
    else:
        command_number = 3
    spectrometer.do_the_call(command_number)
    spectrometer.get_results()
