from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api import views
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

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'settings', views.SettingsViewSet)
router.register(r'sample', views.SampleViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'sample_data', views.SampleDataViewSet)
router.register(r'sample_feature', views.SampleFeatureViewSet)
router.register(r'sample_match', views.SampleMatchViewSet)
router.register(r'photo', views.PhotoViewSet)
router.register(r'voice_memo', views.VoiceMemoViewSet)
router.register(r'sample_delta', views.SampleDeltaViewSet)
router.register(r'group_match_candidate', views.GroupMatchCandidateViewSet)
router.register(r'group_member', views.GroupMemberViewSet)
router.register(r'group_limit', views.GroupLimitViewSet)
router.register(r'location', views.LocationViewSet)
router.register(r'subject', views.SubjectViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
