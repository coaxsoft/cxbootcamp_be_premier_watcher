"""cxbootcamp_django_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Premiers API",
        default_version=settings.DEFAULT_API_VERSION,
        description="Premiers API docs",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_urlpatterns_v1 = [
    path('auth/', include('authentication.urls')),
    path('premiers/', include('premiers.urls')),
    path('static/', include('static_content.urls')),
    path('profile/', include('user_profile.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='docs-redoc-schema-ui'),
    path('v1/', include((api_urlpatterns_v1, 'v1')))
]
