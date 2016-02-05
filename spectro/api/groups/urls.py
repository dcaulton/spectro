from django.conf.urls import url

from spectro.api.groups import views


urlpatterns = [
    url(r'^settings$', views.settings, name='settings'),
]
