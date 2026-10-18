from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),  # доп. задание
]
