from django.urls import path
from . views import *
from dashboard.encrypt_url import urlEncryption, urlEncoding

urlpatterns = [
    path(f"{urlEncryption('signup')}{urlEncoding('signup')}/", signup, name='signup'),
    path(f"{urlEncryption('signout')}{urlEncoding('signout')}/", signout, name='signout'),
]