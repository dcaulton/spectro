from rest_framework import serializers

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


class SettingsSerializer(serializers.ModelSerializer):
    # TODO add custom logic, this is a singleton
    class Meta:
        model = Settings


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group


class SampleDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleData


class SampleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleFeature


class SampleMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleMatch


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image


class VoiceMemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceMemo


class SampleDeltaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleDelta


class GroupMatchCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMatchCandidate


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember


class GroupLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupLimit


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
