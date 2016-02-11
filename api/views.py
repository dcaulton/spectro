import uuid

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


def get_current_group():
    #TODO create settings and group objects if none exist
    if not Settings.objects.count():  # create settings and group if no settings object exists
        group = Group()
        group.save()
        settings = Settings(group=group)
        settings.save()
        return group
    settings = Settings.objects.all()[0]
    group = Group.objects.get(id=settings.current_group_id)
    return group

@api_view()
def capture_sample(request):
    #do these steps asynchronously, return the id of the sample synchronously
    #call spectrometer, save a Sample record
    #call camera, save a Photo record
    #call voice record, save a VoiceMemo record
    #call sample post processing logic
    group = get_current_group()

    sample = take_spectrometer_sample(group)

    if group.use_photo:
        photo = take_photo(group, sample)

    sample_serializer = SampleSerializer(sample)
    photo_serializer = PhotoSerializer(photo)
    composite_data = {'sample': sample_serializer.data,
                      'photo': photo_serializer.data}
    return Response(composite_data)

def take_spectrometer_sample(group):
    sample_id = uuid.uuid4()

    spectrometer = Spectrometer()
    if group.reading_type == Sample.SPECTROMETER:
        sample_data = spectrometer.take_spectrometer_reading()
    if group.reading_type == Sample.COLOR:
        sample_data = spectrometer.take_color_reading()
    if group.reading_type == Sample.FLUORESCENCE:
        sample_data = spectrometer.take_fluorescence_reading()

    average_value = 0
    if sample_data:
        average_value = sum(sample_data) / len(sample_data)
 
    sample = Sample(id=sample_id,
                    group=group,
                    reading_type=group.reading_type,
                    record_type=Sample.PHYSICAL,
                    subject=group.subject,
                    data=sample_data,
                    average_magnitude=average_value)
    sample.save()
    return sample

def take_photo(group, sample):
    photo_id = uuid.uuid4()
    camera = Picam()
    file_path = camera.take_still(str(photo_id)+'.jpg')
    photo = Photo(id=photo_id,
                  group=group,
                  sample=sample,
                  subject=group.subject,
                  file_path=file_path)
    photo.save()
    return photo

@api_view()
def calibrate(request, reference_sample_id):
    sample_id = uuid.uuid4()
    resp_data = {'calibration_delta_id': str(sample_id)}
    return Response(resp_data)

@api_view()
def train(request, sample_name):
    sample_id = uuid.uuid4()
    resp_data = {'sample_id': str(sample_id)}
    return Response(resp_data)
