from django.urls import path

from . import views


app_name = "board" #เพิ่ม namespace สำหรับแอป note
urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('<str:username>/board/', views.kanban_board, name='board'),
    path('<str:username>/add-card/', views.add_card, name='add_card'),  # เพิ่ม username ใน path
    path('<str:username>/update-card/', views.update_card, name='update_card'),
]