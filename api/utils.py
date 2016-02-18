import functools
import uuid

from django.shortcuts import get_object_or_404

from api.camera import Picam
from api.models import (Sample,
                        Settings,
                        Group,
                        Image,
                        SampleData,
                        )
from api.spectrometer import Spectrometer


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

def create_sample_delta(delta_id, group_id, source_sample_id, reference_sample_id):
    '''
    Compare the data between two samples
    Return a SampleDelta object with what needs to be added to the source sample to get the reference sample
    '''
    diff_data = []
    source_sample = Sample.objects.get(id=source_sample_id)
    reference_sample = Sample.objects.get(id=reference_sample_id)
    reference_sample_array = reference_sample.data.split(',')
    source_sample_array = source_sample.data.split(',')

    for (index, source_val) in enumerate(source_sample_array):
        diff_data.append(int(reference_sample_array[index]) - int(source_val))

    diff_data_csv_string = int_list_to_csv_string(diff_data)
    sample_delta = SampleDelta(id=delta_id,
                               group_id=group_id,
                               source_sample=source_sample,
                               reference_sample=reference_sample,
                               data=diff_data_csv_string)
    sample_delta.save()
    return sample_delta

def get_average_sample_value(sample_data):
    '''
    Find the int average of all the values in a sample data (an array of ints)
    '''
    average_value = 0
    if sample_data:
        average_value = sum(sample_data) / len(sample_data)
    return average_value
 
def take_spectrometer_sample(sample_id=uuid.uuid4(),
                             group_id=None,
                             reading_type=Sample.SPECTROMETER,
                             subject=None,
                             description=''):
    '''
    Call the Spectrometer class to gather a sample from the hardware
    Returns a Sample object
    '''
    spectrometer = Spectrometer()
    if reading_type == Sample.SPECTROMETER:
        sample_data = spectrometer.take_spectrometer_reading()
    if reading_type == Sample.COLOR:
        sample_data = spectrometer.take_color_reading()
    if reading_type == Sample.FLUORESCENCE:
        sample_data = spectrometer.take_fluorescence_reading()

    sample_data_csv_string = int_list_to_csv_string(sample_data)
    average_value = get_average_sample_value(sample_data)

    the_subject = subject
    if group_id:
        group = Group.objects.get(id=group_id)
        if group and group.subject:  #TODO add logic that tests this condition
            the_subject = group.subject

    sample = Sample(id=sample_id,
                    group_id=group_id,
                    reading_type=reading_type,
                    record_type=Sample.PHYSICAL,
                    description=description,
                    subject=the_subject,
                    data=sample_data_csv_string,
                    average_magnitude=average_value)
    sample.save()
    return sample

def int_list_to_csv_string(array_of_ints):
    '''
    Convert an array of ints into a single string with all the ints separated by commas
    '''
    return functools.reduce(lambda x, y: str(x)+','+str(y), array_of_ints)

def take_photo(photo_id, group, sample_id):
    '''
    Calls the Picam class to have the hardware take a picture.
    Returns a Picture object
    '''
    camera = Picam()
    file_path = camera.take_still(str(photo_id)+'.jpg')
    image = Image(id=photo_id,
                  group=group,
                  sample_id=sample_id,
                  subject=group.subject,
                  file_path=file_path)
    image.save()
    return image

def extract_features(sample_id=None):
    sample = get_object_or_404(Sample, id=sample_id)
    print('Extract Features: sample data is '+str(sample.data))
    print('Extract Features: sample average magnitude is '+str(sample.average_magnitude))
