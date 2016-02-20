import os
import uuid

from django.shortcuts import get_object_or_404
import matplotlib.pyplot as plt

from api.camera import Picam
from api.models import (Sample,
                        Settings,
                        Group,
                        Image,
                        SampleData,
                        SampleDelta,
                        )
from api.spectrometer import Spectrometer
from api.utils import (csv_string_to_int_list,
                       get_average_sample_value,
                       get_current_group,
                       int_list_to_csv_string,
                       )


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
        if group and group.subject:  # TODO add logic that tests this condition
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


def take_photo(photo_id, group, sample_id):
    '''
    Calls the Picam class to have the hardware take a picture.
    Returns a Picture object
    '''
    camera = Picam()
    file_path = camera.take_still(str(photo_id) + '.jpg')
    image = Image(id=photo_id,
                  group=group,
                  sample_id=sample_id,
                  type=Image.PHOTO,
                  subject=group.subject,
                  file_path=file_path)
    image.save()
    return image


def generate_chart(sample_id, image_id):
    sample = get_object_or_404(Sample, id=sample_id)
    readings = csv_string_to_int_list(sample.data)

    the_title = 'Readings for ' + sample.reading_type + ' sample ' + str(sample_id)
    if sample.description:
        the_title += "\n" + sample.description

    x = range(len(readings))
    plt.bar(x, readings, 1, color='black')
    plt.title(the_title)
    plt.xlabel('wavelength (340 - 780nm)')
    plt.ylabel('magnitude')

    root_directory = '/home/pi/Pictures'  # TODO move this into settings:IMAGE_SAVE_PATH
    file_path = os.path.join(root_directory, (str(image_id) + '.png'))
    image = Image(id=image_id,
                  group=sample.group,
                  sample_id=sample_id,
                  type=Image.BAR_CHART,
                  file_path=file_path)
    image.save()  # save the image record
    plt.savefig(file_path)  # save the actual file with the image
