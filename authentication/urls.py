from django.urls import path

from authentication import views

app_name = 'auth'

urlpatterns = [
    path('', views.ObtainJSONWebToken.as_view(), name='auth'),
    path('verify/', views.VerifyJSONWebToken.as_view(), name='auth-verify'),
    path('refresh/', views.RefreshJSONWebToken.as_view(), name='auth-refresh'),
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('activate/', views.ActivateUserView.as_view(), name='activate'),
    path('reset/', views.ResetPasswordView.as_view(), name='reset'),
    path('restore/', views.RestorePasswordView.as_view(), name='restore'),
]