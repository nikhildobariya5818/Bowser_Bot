from django.urls import path
from .views import visit_url

urlpatterns = [
    path('visit/', visit_url, name='visit_url'),
]
