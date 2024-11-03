"""
ASGI config for project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import os
from fastapi import FastAPI
from .api.routers import api_router, get_status  # Importez vos routes FastAPI
from whitenoise import WhiteNoise
from django.conf import settings

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_asgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

django_asgi_app = get_asgi_application()
fastapi_app = FastAPI()

# Montez les routes FastAPI
fastapi_app.include_router(api_router, prefix="/api")


# Application principale ASGI
async def app(scope, receive, send):
    if scope['type'] == 'http':
        # D'abord vérifier les routes FastAPI
        if scope['path'].startswith("/api") or scope['path'].startswith("/docs") or scope['path'].startswith("/redoc") or scope['path'].startswith("/openapi.json"):
            await fastapi_app(scope, receive, send)
        else:
            # Ensuite, laisser Django gérer les autres requêtes
            await django_asgi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)