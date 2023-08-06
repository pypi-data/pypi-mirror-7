from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('')

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )

if 'test_app' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'', include('test_app.urls')),
    )

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS and settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
