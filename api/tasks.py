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



#take_spectrometer_task(sample_id, group)
def take_spectrometer_task(sample_id, group):
    take_spectrometer_sample_task_id = async(take_spectrometer_sample,
                                             sample_id,
                                             group.id,
                                             group.reading_type)
    return take_spectrometer_sample_task_id

#calibrate_task(source_sample_id, delta_id, group, request.query_params['reference_sample_id'])
def calibrate_task(source_sample_id, delta_id, group, reference_sample_id):
    chain = Chain(cached=True)
    chain.append(take_spectrometer_sample, source_sample_id, group.id, group.reading_type)
    chain.append(create_sample_delta, delta_id, group.id, source_sample_id, reference_sample_id)
    chain.run()

#train_task(sample_id, request.query_params['reading_type'], request.query_params['sample_name'])
def train_task(sample_id, reading_type, sample_name)
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
