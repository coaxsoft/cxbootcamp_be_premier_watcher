from django.urls import path

from user_profile import views

app_name = 'user_profile'

urlpatterns = [
    path('', views.ProfileViewSet.as_view({
        'get': 'retrieve',
    }), name='profile'),
    path('password/change/', views.ProfileViewSet.as_view({"post": "change_password"}),
         name='password-change'),
    path('deactivate/', views.ProfileViewSet.as_view({"post": "deactivate"}),
         name='deactivate'),
    path('email/', views.ProfileViewSet.as_view({"patch": "change_email"}),
         name='email'),
]
