from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("genre/<slug:slug>/", views.genre_page, name="genre_page"),
    path("anime/<str:anime_id>/", views.anime_detail, name="anime_detail"),

    path("login/", auth_views.LoginView.as_view(template_name="myapp/auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path('accounts/profile/', views.profile, name='profile')
]
