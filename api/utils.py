import functools
import os

from django.conf import settings
from django.shortcuts import get_object_or_404

from api.exceptions import SpectrometerConnectionError
from api.models import Group, Settings


def get_error_string_for_api(exception):
    return exception.__class__.__name__ + ' : ' + str(exception)


def requires_connected_spectrometer(func):
    '''
    Decorator that checks if the Arduino is plugged in at the expected mount point
    '''
    def requires_connected_spectrometer_and_call(*args, **kwargs):
        if not spectrometer_is_connected():
            raise SpectrometerConnectionError('Spectrometer host Arduino is not plugged in')
        return func(*args, **kwargs)
    return requires_connected_spectrometer_and_call
    

def spectrometer_is_connected():
    if os.path.exists(settings.SPECTROMETER_MOUNT_POINT):
        return True
    return False


def get_current_group():
    '''
    Get the group pointed to by the settings object.  Settings is a singleton.
    If settings doesn't exist, create settings and group.
    '''
    if not Settings.objects.count():  # create settings and group if no settings object exists
        group = Group()
        group.save()
        settings = Settings(group=group)
        settings.save()
        return group
    settings = Settings.objects.all()[0]
    group = get_object_or_404(Group, id=settings.current_group_id)
    return group


def get_average_sample_value(sample_data):
    '''
    Find the int average of all the values in a sample data (an array of ints)
    '''
    average_value = 0
    if sample_data:
        average_value = sum(sample_data) / len(sample_data)
    return average_value


def int_list_to_csv_string(array_of_ints):
    '''
    Convert an array of ints into a single string with all the ints separated by commas
    '''
    return functools.reduce(lambda x, y: str(x) + ',' + str(y), array_of_ints)


def csv_string_to_int_list(csv_string):
    int_arr = [int(v) for v in csv_string.split(',')]
    return int_arr
