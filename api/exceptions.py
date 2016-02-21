from rest_framework.exceptions import APIException


class SpectroBaseError(APIException):

    """
    Invalid request at the resource or parameter level; the client is using the API wrong.
    """
    status_code = 400


class SpectrometerConnectionError(SpectroBaseError):
    '''
    The spectrometer is not connected or is not responding to calls.
    '''
    detail = 'Spectrometer host Arduino is not plugged in'


class SpectrometerRetriesError(SpectroBaseError):

    """
    The Spectrometer is not responding to calls on the serial port
    """
    detail = 'exceeded max number of retries when calling spectrometer'
