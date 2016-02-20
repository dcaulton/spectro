import uuid

from django_q.tasks import async, Chain

from api.services import (create_sample_delta,
                          generate_chart,
                          get_current_group,
                          take_photo,
                          take_spectrometer_sample,
                          )


def capture_sample_task(group):
    '''
    Handles asynchronous calling of the spectrometer to take a reading
    Optionally chains tasks for taking a photo and generating a chart, depending on group config
    '''
    sample_id = uuid.uuid4()
    return_dict = {'sample_id': sample_id}

    chain = Chain(cached=True)
    chain.append(take_spectrometer_sample,
                 sample_id=sample_id,
                 group_id=group.id,
                 reading_type=group.reading_type)

    if group.generate_chart:
        chart_id = uuid.uuid4()
        chain.append(generate_chart,
                     sample_id=sample_id,
                     image_id=chart_id)
        return_dict['chart_id'] = chart_id

    if group.use_photo:
        photo_id = uuid.uuid4()
        chain.append(take_photo,
                     photo_id,
                     group,
                     sample_id)
        return_dict['photo_id'] = photo_id

    chain.run()
    return return_dict


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
    chain.append(generate_chart,
                 sample_id=sample_id)
    chain.run()
