"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
As you know, every app must be hooked into your main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from test_app.views import HomeView

admin.autodiscover()

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns(
    '',
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^positions/', include('generic_positions.urls')),
    url(r'^user_media/', include('user_media.urls')),
    url(r'^$', HomeView.as_view()),
)
