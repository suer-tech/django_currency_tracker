from django.urls import path
from .views import get_current_usd, index


urlpatterns = [
    path('get-current-usd/', get_current_usd, name='get_current_usd'),
    path('', index, name='index'),
]

