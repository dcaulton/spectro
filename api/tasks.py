from django_q.tasks import async, Chain

from api.services import (create_sample_delta,
                          extract_features,
                          get_current_group,
                          take_photo,
                          take_spectrometer_sample,
                         )


def take_spectrometer_task(sample_id, group):
    '''
    Handles asynchronous calling of the spectrometer to take a reading
    '''
    take_spectrometer_sample_task_id = async(take_spectrometer_sample,
                                             sample_id,
                                             group.id,
                                             group.reading_type)
    return take_spectrometer_sample_task_id

def calibrate_task(source_sample_id, delta_id, group, reference_sample_id):
    '''
    Handles asynchronous processing of all the tasks required for a calibration reading 
    '''
    chain = Chain(cached=True)
    chain.append(take_spectrometer_sample, source_sample_id, group.id, group.reading_type)
    chain.append(create_sample_delta, delta_id, group.id, source_sample_id, reference_sample_id)
    chain.run()

def train_task(sample_id, reading_type, sample_name):
    '''
    Handles asynchronous processing of all the tasks required to train the spectrometer on a substance
    '''
    chain = Chain(cached=True)
    chain.append(take_spectrometer_sample,
                 sample_id=sample_id,
                 group_id=None,
                 reading_type=reading_type,
                 subject=None,
                 description=sample_name)
    chain.append(extract_features,
                 sample_id=sample_id)
    chain.run()

def take_photo_task(photo_id, group, sample_id):
    '''
    Handles asynchronous processing of all the tasks needed to take a photo with the Raspberry Pi camera
    '''
    take_photo_task_id = async(take_photo, photo_id, group, sample_id)
    return take_photo_task_id
