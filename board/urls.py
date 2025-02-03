from django.urls import path

from . import views


app_name = "board" #เพิ่ม namespace สำหรับแอป note
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('<str:username>/categories/', views.list_categories, name='categories'),
    path('<str:username>/create-category/', views.create_category, name='create_category'),
    path('<str:username>/category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('<str:username>/category/<int:category_id>/create-topic/', views.create_topic, name='create_topic'),
    path('<str:username>/topic/<int:topic_id>/board/', views.kanban_board, name='board'),
    path('<str:username>/add-card/', views.add_card, name='add_card'),
    path('<str:username>/update-card/', views.update_card, name='update_card'),
    path('logout/', views.logout_view, name='logout'),
]