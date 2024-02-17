from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('rooms/<int:id>', views.rooms, name = 'rooms'),
    path('create_room',views.create_room,name = "create_room"),
    path('update_room/<int:pk>/',views.update_room,name = 'update_room'),
    path('delete_room/<int:pk>',views.delete_room,name = 'delete_room'),
    path('delete_message/<int:pk>/<int:room_id>/',views.delete_message, name = 'delete_message'),
    path("user_profile/<int:id>",views.user_profile,name = 'profile'),
    path('register/',views.register_view,name = 'register'),
    path('login/',views.login_view,name = 'login'),
    path('logout/',views.logout_view, name = 'logout'),
]
