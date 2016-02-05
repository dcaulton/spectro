from django.conf.urls import url

from spectro.api.groups import views


urlpatterns = [
    url(r'^groups$', views.GroupListView.as_view(), name='group_list'),
    url(r'^groups/(?P<group_id>[\w-]+)$', views.GroupDetailView.as_view(), name='group_detail'),
]
