import tempfile
from core.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_ROOT = tempfile.mkdtemp(prefix='test-media-')

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
