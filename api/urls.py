from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api import views
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

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'settings', views.SettingsViewSet)
router.register(r'samples', views.SampleViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'sample_datas', views.SampleDataViewSet)
router.register(r'sample_features', views.SampleFeatureViewSet)
router.register(r'sample_matchs', views.SampleMatchViewSet)
router.register(r'photos', views.ImageViewSet)
router.register(r'voice_memos', views.VoiceMemoViewSet)
router.register(r'sample_deltas', views.SampleDeltaViewSet)
router.register(r'group_match_candidates', views.GroupMatchCandidateViewSet)
router.register(r'group_members', views.GroupMemberViewSet)
router.register(r'group_limits', views.GroupLimitViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'subjects', views.SubjectViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/capture_sample/', views.capture_sample),
    url(r'^api/v1/calibrate/', views.calibrate),
    url(r'^api/v1/train/', views.train),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
