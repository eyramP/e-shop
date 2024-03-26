from django.urls import path
from .import views

urlpatterns = [
    path("register/", views.register, name="register_user"),
    path("me/", views.current_user, name="current_user"),
    path("me/update/", views.update_profile, name="current_user"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("<str:token>/reset_password/", views.reset_password, name="reset_password"),
]
