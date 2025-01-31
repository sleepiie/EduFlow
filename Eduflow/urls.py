from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include('board.urls', namespace='board')),
    path("admin/", admin.site.urls),
]


