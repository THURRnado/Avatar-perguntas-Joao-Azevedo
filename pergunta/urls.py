from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('filtro/<str:genero>/', views.filtro_genero, name='filtro_genero'),
    path('escolher/<int:pk>/', views.escolher, name="escolher"),
    path('confirmar_pergunta/', views.confirmar_pergunta, name='confirmar_pergunta'),
    path('comunicacao_ia/', views.comunicacao_ia, name="comunicacao_ia"),
    path("api/avatar/retorno/", views.avatar_retorno, name="avatar_retorno"),
]
