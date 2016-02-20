from rest_framework.exceptions import APIException


class SpectroBaseError(APIException):

    """
    Invalid request at the resource or parameter level; the client is using the API wrong.
    """
    status_code = 400


class SpectrometerSerialError(SpectroBaseError):

    """
    The Spectrometer is not responding to calls on the serial port
    """
    status_code = 400
    detail = 'exceeded max number of retries when calling spectrometer'
