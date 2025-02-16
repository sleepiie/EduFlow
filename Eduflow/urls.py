from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path('', include('board.urls', namespace='board')),
    path("admin/", admin.site.urls),
]


