from django.urls import path
from . import views

urlpatterns = [
    path('author/', views.author_view, name='author'),
    path('about/', views.about_view, name='about'),
    path('', views.home_view, name='home'),
]