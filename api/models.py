import uuid

from django.db import models, transaction
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


class Group(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1024)
    created = AutoCreatedField()

    class Meta:
        db_table = 'group'


class Settings(SingletonModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    group_id = models.ForeignKey(Group)

    class Meta:
        db_table = 'settings'
