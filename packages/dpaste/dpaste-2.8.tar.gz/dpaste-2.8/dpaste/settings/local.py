from dpaste.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Your Name', 'name@example.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dpaste',
        'USER': 'root',
        'PASSWORD': '',
    }
}

SECRET_KEY = 'changeme'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
