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
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    current_group = models.ForeignKey(Group)

    class Meta:
        db_table = 'settings'


class Group(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1024)
    created = AutoCreatedField()
    parent_group = models.ForeignKey(Group)
    calibration = models.ForeignKey(Calibration)
    subject = models.ForeignKey(Subject)
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

class Sample(models.Model):
    SPECTROMETER = 'spectro'
    COLOR = 'color'
    FLUORESCENCE = 'fluoro'
    READING_TYPE_CHOICES = (
        (SPECTROMETER, 'Spectrometer'),
        (COLOR, 'Color'),
        (FLUORESCENCE, 'Fluorescence'),
    )

    FIND_MATCH = 'find_match'
    CHECK_LIMITS = 'check_limits'
    NONE = 'none'
    POST_CAPTURE_PROCESSING_CHOICES = (
        (FIND_MATCH, 'Search for a match'),
        (CHECK_LIMITS, 'Compare to upper and lower limits'),
        (NONE, 'No post capture processing'),
    )

class GroupMatchCandidate(models.Model):
    group_id_of_sample = models.ForeignKey(Group)
    group_id_of_reference_sample = models.ForeignKey(Group)

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
    group = models.ForeignKey(Group)
    owner = models.ForeignKey(User)
    role = models.CharField(max_length=32, Choices=ROLE_CHOICES)
