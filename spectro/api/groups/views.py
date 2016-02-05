import datetime

from django.db import transaction
from rest_framework.response import Response
from rest_framework import serializers, status

from spectro.api.groups.models import Group
from spectro.api.views import SpectroApiView

class GroupSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)

class GroupListView(SpectroApiView):

    def get(self, request):
        the_groups = [
            {"id": "1233",
             "name": "fungus among us",
             "created": datetime.datetime.now()
            },
            {"id": "4566",
             "name": "sometimes yes",
             "created": datetime.datetime.now()
            }
        ]
        serializer = GroupSerializer(the_groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GroupDetailView(SpectroApiView):

    def get(self, request, group_id):
        the_group = {
            "id": "5677",
            "created": datetime.datetime.now()
        }
        serializer = GroupSerializer(the_group)
        return Response(serializer.data)
