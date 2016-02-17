import uuid

from django.shortcuts import get_object_or_404
from django_q.tasks import async, Chain
from rest_framework import viewsets
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

from api.models import (Settings,
                        Sample,
                        Group,
                        SampleData,
                        SampleFeature,
                        SampleMatch,
                        Image,
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
                             ImageSerializer,
                             VoiceMemoSerializer,
                             SampleDeltaSerializer,
                             GroupMatchCandidateSerializer,
                             GroupMemberSerializer,
                             GroupLimitSerializer,
                             LocationSerializer,
                             SubjectSerializer,
                            )
from api.utils import (create_sample_delta,
                       extract_features,
                       get_current_group,
                       take_photo,
                       take_spectrometer_sample,
                      )



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


class ImageViewSet (viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


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
    Both capture tasks are run asynchronously, the sample_id, photo_id, and task ids for both captures are returned
    '''

    group = get_current_group()
    sample_id = uuid.uuid4()

    take_spectrometer_sample_task_id = async(take_spectrometer_sample,
                                             sample_id,
                                             group.id,
                                             group.reading_type)

    composite_data = {'sample': {'id': sample_id, 'task_id': take_spectrometer_sample_task_id}}

    if group.use_photo:
        photo_id = uuid.uuid4()
        take_photo_task_id = async(take_photo, photo_id, group, sample_id)
        composite_data['photo'] = {'id': photo_id, 'task_id': take_photo_task_id}

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
        source_sample_id = uuid.uuid4()
        delta_id = uuid.uuid4()
        chain = Chain(cached=True)
        chain.append(take_spectrometer_sample, source_sample_id, group.id, group.reading_type)
        chain.append(create_sample_delta, delta_id, group.id, source_sample_id, request.query_params['reference_sample_id'])
        chain.run()
        composite_data = {'sample': {'id': source_sample_id},
                          'sample_delta': {'id': delta_id}}

        return Response(composite_data)
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
            chain = Chain(cached=True)
            chain.append(take_spectrometer_sample,
                         sample_id=sample_id,
                         group_id=None,
                         reading_type=request.query_params['reading_type'],
                         subject=None,
                         description=request.query_params['sample_name'])
            chain.append(extract_features,
                         sample_id=sample_id)
            chain.run()
            composite_data = {'sample': {'id': sample_id}}
            return Response(composite_data)
        else: #TODO add a test for this condition
            err_message = 'A non-empty sample name must be specified for a reference sample'
            return Response(data=err_message, status=409)
    else:
        #TODO add a test for this condition
        err_message = 'Invalid sample type, must be one of these: '+str(valid_sample_types)
        return Response(data=err_message, status=409)
