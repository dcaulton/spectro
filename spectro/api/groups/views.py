import datetime

from django.db import transaction
from django.http import HttpResponse

from spectro.api.groups.models import Group, Settings
from spectro.api.views import SpectroApiView

def settings(request):
    if request.method == 'GET':
        the_response = 'here are the settings, buddy'
    if request.method == 'PUT':
        import uuid
        s = Settings(id=str(uuid.uuid4()), group_id=str(uuid.uuid4()))
        s.save()
        the_response = 'saving your settings, funny guy'
    
    return HttpResponse(the_response)
