"""Settings that need to be set in order to run the tests."""
import os


DJANGO_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

DEBUG = True
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'user_media.tests.urls'

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(DJANGO_PROJECT_ROOT, '../media')
STATIC_ROOT = os.path.join(DJANGO_PROJECT_ROOT, '../static')
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(DJANGO_PROJECT_ROOT, 'static'),
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates'),
)

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), 'coverage')
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'test_app', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

EXTERNAL_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_jasmine',
    'django_nose',
    'easy_thumbnails',
    'django_libs',
    'generic_positions',
]

INTERNAL_APPS = [
    'user_media',
    'user_media.tests.test_app',
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS
COVERAGE_MODULE_EXCLUDES += EXTERNAL_APPS

SECRET_KEY = 'xxx'

THUMBNAIL_PROCESSORS = (
    'user_media.processors.crop_box',
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
)
