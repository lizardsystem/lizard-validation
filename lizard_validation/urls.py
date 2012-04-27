# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^diff/(?P<area_name>.*)/(?P<config_type>.*)',
        'lizard_validation.views.view_config_diff',
        name="diff"),
    )
urlpatterns += debugmode_urlpatterns()
