from django.urls import path

from static_content.views import ImageUploadView

app_name = 'static_content'

urlpatterns = [
    path('image/', ImageUploadView.as_view(), name='image-upload'),
]
