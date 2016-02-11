import uuid

from django.db import models, transaction
from django.contrib.auth.models import User
from model_utils.fields import AutoCreatedField

#Thank you Senko Rašić: http://goodcode.io/articles/django-singleton-models/
class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class Settings(SingletonModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    current_group = models.ForeignKey('Group')

    class Meta:
        db_table = 'settings'


class Sample(models.Model):
    SPECTROMETER = 'spectro'
    COLOR = 'color'
    FLUORESCENCE = 'fluoro'
    READING_TYPE_CHOICES = (
        (SPECTROMETER, 'Spectrometer'),
        (COLOR, 'Color'),
        (FLUORESCENCE, 'Fluorescence'),
    )

    PHYSICAL = 'Physical' #taken from this spectrometer
    VIRTUAL = 'Virtual' #estimated from physical data of an untested compound
    DERIVED = 'Defined' #created from merging samples
    RECORD_TYPE_CHOICES = (
        (PHYSICAL, 'Physical'),
        (VIRTUAL, 'Virtual'),
        (DERIVED, 'Derived'),
    )

    FIND_MATCH = 'find_match'
    CHECK_LIMITS = 'check_limits'
    NONE = 'none'
    POST_CAPTURE_PROCESSING_CHOICES = (
        (FIND_MATCH, 'Search for a match'),
        (CHECK_LIMITS, 'Compare to upper and lower limits'),
        (NONE, 'No post capture processing'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    group = models.ForeignKey('Group', null=True)
    reading_type = models.CharField(max_length=32, choices=READING_TYPE_CHOICES)
    record_type = models.CharField(max_length=32, choices=RECORD_TYPE_CHOICES)
    description = models.CharField(max_length=4096)
    subject = models.ForeignKey('Subject', null=True)
    data = models.CharField(max_length=4096)
    average_magnitude = models.IntegerField(default=0)
    representative_sample = models.ForeignKey('Sample', null=True)

    class Meta:
        db_table = 'sample'


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    name = models.CharField(max_length=1024, null=True)
    parent_group = models.ForeignKey('Group', null=True)
    subject = models.ForeignKey('Subject', null=True)
    reading_type = models.CharField(max_length=32,
                                    choices=Sample.READING_TYPE_CHOICES,
                                    default=Sample.SPECTROMETER)
    use_voice_memo = models.BooleanField()
    use_photo = models.BooleanField()
    post_capture_processing = models.CharField(max_length=32,
                                               choices=Sample.POST_CAPTURE_PROCESSING_CHOICES,
                                               default=Sample.FIND_MATCH)
    try_composite_candidates = models.BooleanField()

    class Meta:
        db_table = 'group'


class SampleData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey('Sample', null=True)
    delta = models.ForeignKey('SampleDelta', null=True)
    frequency = models.IntegerField()
    magnitude = models.IntegerField()

    class Meta:
        db_table = 'sample_data'


class SampleFeature(models.Model):
    PEAK = 'peak'
    VALLEY = 'valley'
    SPIKE = 'spike'
    HOLE = 'hole'
    PLATEAU_START = 'plateau_start'
    PLATEAU_END = 'plateau_end'
    FEATURE_TYPE_CHOICES = (
        (PEAK, 'Peak'),
        (VALLEY, 'Valley'),
        (SPIKE, 'Spike'),
        (HOLE, 'Hole'),
        (PLATEAU_START,'Start of Plateau'),
        (PLATEAU_END, 'End of Plateau'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey('Sample')
    feature_type = models.CharField(max_length=32, choices=FEATURE_TYPE_CHOICES)
    sharpness = models.IntegerField()
    magnitude = models.IntegerField()

    class Meta:
        db_table = 'sample_feature'


class SampleMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_sample = models.ForeignKey('Sample', related_name = 'samplematch_source_sample')
    reference_sample = models.ForeignKey('Sample', related_name = 'samplematch_reference_sample')
    delta = models.ForeignKey('SampleDelta', null=True)
    rating = models.FloatField(default=0.0)

    class Meta:
        db_table = 'sample_match'


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    group = models.ForeignKey('Group', null=True)
    sample = models.ForeignKey('Sample', null=True)
    subject = models.ForeignKey('Subject', null=True)
    file_path = models.CharField(max_length=1024)

    class Meta:
        db_table = 'photo'


class VoiceMemo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    sample = models.ForeignKey('Sample', null=True)
    file_path = models.CharField(max_length=1024)

    class Meta:
        db_table = 'voice_memo'


class SampleDelta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('Group', null=True)
    source_sample = models.ForeignKey('Sample', related_name = 'sampledelta_source_sample', null=True)
    reference_sample = models.ForeignKey('Sample', related_name = 'sampledelta_reference_sample', null=True)

    class Meta:
        db_table = 'sample_delta'


class GroupMatchCandidate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_id_of_sample = models.ForeignKey('Group', related_name = 'source_sample_group')
    group_id_of_reference_sample = models.ForeignKey('Group', related_name = 'reference_sample_group')

    class Meta:
        db_table = 'group_match_candidate'


class GroupMember(models.Model):
    ACCESS_WEBAPP = 'access_webapp'
    RECEIVE_NOTIFICATIONS = 'receive_notifications'
    TAKE_SAMPLES = 'take_samples'
    CONFIGURE_GROUP = 'configure_group'
    ROLE_CHOICES = (
        (ACCESS_WEBAPP, 'Access web application'),
        (RECEIVE_NOTIFICATIONS, 'Receive notifications'),
        (TAKE_SAMPLES, 'Take samples'),
        (CONFIGURE_GROUP, 'Configure group'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    group = models.ForeignKey('Group')
    username = models.CharField(max_length=64)   #make this a foreign key to the Django admin User table
    user = models.ForeignKey('auth.User', related_name='groupmember')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'group_member'


class GroupLimit(models.Model):
    SEND_EMAIL = 'send_email'
    TAKE_ANOTHER_READING = 'take_another_reading'
    NONE = 'none'
    LIMITS_EXCEEDED_ACTION_CHOICES = (
        (SEND_EMAIL, 'Send email to group members'),
        (TAKE_ANOTHER_READING, 'Take another reading'),
        (NONE, 'take no action'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey('Group')
    upper_limit = models.ForeignKey('Sample', related_name = 'upper_limit', null=True)
    lower_limit = models.ForeignKey('Sample', related_name = 'lower_limit', null=True)
    limits_exceeded_action = models.CharField(max_length=32, choices=LIMITS_EXCEEDED_ACTION_CHOICES)

    class Meta:
        db_table = 'group_limit'


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = AutoCreatedField()
    group = models.ForeignKey('Group', null=True)
    sample = models.ForeignKey('Sample', null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    elevation = models.FloatField()
    datetime = models.FloatField()
    number_of_satellites = models.IntegerField()

    class Meta:
        db_table = 'location'


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=4096)

    class Meta:
        db_table = 'subject'


