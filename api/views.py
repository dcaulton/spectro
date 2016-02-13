import functools
import uuid

from django.shortcuts import get_object_or_404
from django_q.tasks import async, result
from rest_framework import viewsets
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

from api.camera import Picam
from api.models import (Settings,
                        Sample,
                        Group,
                        SampleData,
                        SampleFeature,
                        SampleMatch,
                        Photo,
                        VoiceMemo,
                        SampleDelta,
                        GroupMatchCandidate,
                        GroupMember,
                        GroupLimit,
                        Location,
                        Subject,
                       )
from api.serializers import (SettingsSerializer,
                             SampleSerializer,
                             GroupSerializer,
                             SampleDataSerializer,
                             SampleFeatureSerializer,
                             SampleMatchSerializer,
                             PhotoSerializer,
                             VoiceMemoSerializer,
                             SampleDeltaSerializer,
                             GroupMatchCandidateSerializer,
                             GroupMemberSerializer,
                             GroupLimitSerializer,
                             LocationSerializer,
                             SubjectSerializer,
                            )
from api.spectrometer import Spectrometer


class SettingsViewSet (viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer


class SampleViewSet (viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer

class GroupViewSet (viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SampleDataViewSet (viewsets.ModelViewSet):
    queryset = SampleData.objects.all()
    serializer_class = SampleDataSerializer


class SampleFeatureViewSet (viewsets.ModelViewSet):
    queryset = SampleFeature.objects.all()
    serializer_class = SampleFeatureSerializer


class SampleMatchViewSet (viewsets.ModelViewSet):
    queryset = SampleMatch.objects.all()
    serializer_class = SampleMatchSerializer


class PhotoViewSet (viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class VoiceMemoViewSet (viewsets.ModelViewSet):
    queryset = VoiceMemo.objects.all()
    serializer_class = VoiceMemoSerializer


class SampleDeltaViewSet (viewsets.ModelViewSet):
    queryset = SampleDelta.objects.all()
    serializer_class = SampleDeltaSerializer


class GroupMatchCandidateViewSet (viewsets.ModelViewSet):
    queryset = GroupMatchCandidate.objects.all()
    serializer_class = GroupMatchCandidateSerializer


class GroupMemberViewSet (viewsets.ModelViewSet):
    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer


class GroupLimitViewSet (viewsets.ModelViewSet):
    queryset = GroupLimit.objects.all()
    serializer_class = GroupLimitSerializer


class LocationViewSet (viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class SubjectViewSet (viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


@api_view()
def capture_sample(request):
    '''
    Capture a physical sample from the spectrometer according to the parameters specified in the current active group
      from (the settings record)
    Capture a photo as well if the group is configured to capture photos
    Save both records to the db
    '''
    #TODO call voice record, save a VoiceMemo record
    #TODO call sample post processing logic
    #TODO have take_photo also run asynchronously, have it accept photo_id
    group = get_current_group()
    sample_id = uuid.uuid4()

    sample = take_spectrometer_sample(sample_id=sample_id,
                                      group_id=group.id,
                                      reading_type=group.reading_type)

    if group.use_photo:
        photo = take_photo(group, sample_id)

    sample_serializer = SampleSerializer(sample)
    photo_serializer = PhotoSerializer(photo)
    composite_data = {'sample': sample_serializer.data,
                      'photo': photo_serializer.data}
    return Response(composite_data)

@api_view()
def capture_sample_async(request):
    '''
    Capture a physical sample from the spectrometer according to the parameters specified in the current active group
      from (the settings record)
    Capture a photo as well if the group is configured to capture photos
    Save both records to the db
    '''

    group = get_current_group()
    sample_id = uuid.uuid4()

    take_spectrometer_sample_task_id = async(take_spectrometer_sample, sample_id, group.id, group.reading_type)

    composite_data = {'sample_id': sample_id, 'task_id': take_spectrometer_sample_task_id}
    return Response(composite_data)

@api_view()
def calibrate(request):
    '''
    Take a sample according to the current group config.
    Compare its data to the reference_sample_id passed in as a get parm
    On success return a SampleDelta object with the differences between the two samples
    '''
    # TODO add logic and tests for null reference_sample_id
    group = get_current_group()

    if 'reference_sample_id' in request.query_params and request.query_params['reference_sample_id']:
        reference_sample = get_object_or_404(Sample, id=request.query_params['reference_sample_id'])
        source_sample = take_spectrometer_sample(group_id=group.id,
                                                 reading_type=group.reading_type)

        delta = create_sample_delta(group, source_sample, reference_sample)

        sample_delta_serializer = SampleDeltaSerializer(delta)

        return Response(sample_delta_serializer.data)
    else:  #TODO add a test for this condition
        err_message = 'An id must be specified for a reference sample'
        return Response(data=err_message, status=409)

@api_view()
def train(request):
    '''
    Take a physical sample from the spectrometer of the reading type specified via the 'reading_type' get parameter.
    Save the record with no group, and a description as specified with the sample_name get parameter.
    This is intended to be a reference sample across all groups.
    On success return json representing the new Sample
    '''
    valid_sample_types = [Sample.SPECTROMETER, Sample.COLOR, Sample.FLUORESCENCE]
    if 'reading_type' in request.query_params and request.query_params['reading_type'] in valid_sample_types:
        if request.query_params['sample_name']:
            sample_id = uuid.uuid4()
            sample = take_spectrometer_sample(sample_id=sample_id,
                                              group_id=None,
                                              reading_type=request.query_params['reading_type'],
                                              subject=None,
                                              description=request.query_params['sample_name'])
            sample_serializer = SampleSerializer(sample)
            return Response(sample_serializer.data)
        else: #TODO add a test for this condition
            err_message = 'A non-empty sample name must be specified for a reference sample'
            return Response(data=err_message, status=409)
    else:
        #TODO add a test for this condition
        err_message = 'Invalid sample type, must be one of these: '+str(valid_sample_types)
        return Response(data=err_message, status=409)

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

def create_sample_delta(group, source_sample, reference_sample):
    '''
    Compare the data between two samples
    Return a SampleDelta object with what needs to be added to the source sample to get the reference sample
    '''
    diff_data = []
    reference_sample_array = reference_sample.data.split(',')
    source_sample_array = source_sample.data.split(',')

    for (index, source_val) in enumerate(source_sample_array):
        diff_data.append(int(reference_sample_array[index]) - int(source_val))

    diff_data_csv_string = int_list_to_csv_string(diff_data)
    sample_delta = SampleDelta(group=group,
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

def take_photo(group, sample_id):
    '''
    Calls the Picam class to have the hardware take a picture.
    Returns a Picture object
    '''
    photo_id = uuid.uuid4()
    camera = Picam()
    file_path = camera.take_still(str(photo_id)+'.jpg')
    photo = Photo(id=photo_id,
                  group=group,
                  sample_id=sample_id,
                  subject=group.subject,
                  file_path=file_path)
    photo.save()
    return photo
