import uuid

from django.db import models
from model_utils.fields import AutoCreatedField

class Group(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=1024)
    created = AutoCreatedField()
