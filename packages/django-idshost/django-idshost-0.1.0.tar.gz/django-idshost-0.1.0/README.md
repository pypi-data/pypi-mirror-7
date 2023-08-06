# django-idshost

Django app to integrate your project in the ids infrastructure.

### Installation

You can get django-idshost from PyPi:
```bash
pip install django-idshost
```

### Configure

To use the app you should add it to your `INSTALLED_APPS` in `settings.py`.

```python
INSTALLED_APPS = (
    ...  
    'django_idshost',
    ...
)
```

Django-idshost custom the backend, the midleware and the model of the django user, so you have to override these datas in the `settings.py`.

```python
AUTHENTICATION_BACKENDS = (
    'django_idshost.auth.idsauth.IdsRemoteUserBackend', #use to authenticate an ids user
    'django.contrib.auth.backends.ModelBackend',#if you want to keep the default authentication, keep this line  
)

MIDDLEWARE_CLASSES = (
    ...
    'django_idshost.auth.idsauth.IdsHeaderMiddleware',#allow the specific http header use by ids to transmit the authenticate user
    ...
)

AUTH_USER_MODEL = 'django_idshost.IdsUser'

```

You should also add your ids datas in the `settings.py`. These datas are transmited by ids.

```python
DJANGO_IDSHOST_SETTINGS = {
    'APP_NAME': '...', #the name of the app 'xxx.idshost.fr'
    'PRIVATE_IP': '...',#the private ip of your server in the ids infrastructure
}
```



