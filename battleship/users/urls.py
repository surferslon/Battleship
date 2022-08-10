from django.urls import path
from users import views

urlpatterns = [
    path("signup", views.CreateUserView.as_view(), name="create_user"),
    path("login", views.LoginView.as_view(), name="login"),
]
