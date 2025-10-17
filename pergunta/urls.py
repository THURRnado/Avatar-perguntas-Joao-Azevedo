from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('filtro/<str:genero>/', views.filtro_genero, name='filtro_genero'),
    path('escolher/<int:pk>/', views.escolher, name="escolher"),
]
