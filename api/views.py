import uuid

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Group, Settings

class SettingsSerializer(serializers.Serializer):
    class Meta:
        model = Settings
        fields = ('group_id')
    
class GroupSerializer(serializers.Serializer):
    class Meta:
        model = Group
        fields = ('name', 'created')

class SettingsView(APIView):
    def get(self, request):
        settings = {'id': uuid.uuid4(), 'group': uuid.uuid4()}
        serializer = SettingsSerializer(settings)
        return Response(serializer.data)

class GroupListView(APIView):
    def get(self, request):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups)
        return Response(serializer.data)

# Create your views here.
#def settings(request):
#    if request.method == 'GET':
#        settings = Settings.object.get()
#    import pdb; pdb.set_trace()
#    pass
