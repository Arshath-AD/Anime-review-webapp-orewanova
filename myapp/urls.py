from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("genre/", views.genre_list, name="genre_list"),
    path("genre/<slug:slug>/", views.genre_page, name="genre_page"),
    path("anime/<str:anime_id>/", views.anime_detail, name="anime_detail"),
    path("anime/<str:anime_id>/rate/", views.rate_anime, name="rate_anime"),
    path("anime/<str:anime_id>/comment/", views.add_comment, name="add_comment"),

    path("api/search/", views.search_api, name="search_api"),
    path("api/search/genre/", views.search_genre, name="search_genre"),

    path("login/", auth_views.LoginView.as_view(template_name="myapp/auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),

    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/add-anime/", views.add_anime, name="add_anime"),
    path("admin-panel/anime/", views.admin_anime_list, name="admin_anime_list"),
    path("admin-panel/anime/edit/<str:anime_id>/", views.edit_anime, name="edit_anime"),
    path("admin-panel/anime/delete/<str:anime_id>/", views.delete_anime, name="delete_anime"),
    path("admin-panel/manage_content/", views.manage_content, name="manage_content"),

]
