from django.contrib import admin
from django.urls import include, path

from .yasg import urlpatterns as doc_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/tests/', include('language_tests.urls')),
]

urlpatterns += doc_urlpatterns
