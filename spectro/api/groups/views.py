import datetime

from rest_framework.response import Response
from rest_framework import serializers

from spectro.api.views import SpectroApiView

class GroupSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)

class GroupListView(SpectroApiView):

    def get(self, request):
        the_groups = [
            {"id": "1233",
            "created": datetime.datetime.now()
            },
            {"id": "4566",
            "created": datetime.datetime.now()
            }
        ]
        serializer = GroupSerializer(the_groups, many=True)
        return Response(serializer.data)

class GroupDetailView(SpectroApiView):

    def get(self, request, group_id):
        the_group = {
            "id": "5677",
            "created": datetime.datetime.now()
        }
        serializer = GroupSerializer(the_group)
        return Response(serializer.data)
