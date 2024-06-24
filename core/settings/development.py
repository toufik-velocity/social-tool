from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('DB'),
    }
}


MONGODB_DATABASES = {
    'default': {
        'name': os.getenv('DB'),
        'host': f"{os.getenv('CLIENT')}{os.getenv('DB')}",
    }
}