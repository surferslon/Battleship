from django.urls import path
from games import views

urlpatterns = [
    path("list", views.GameListView().as_view(), name="games_list"),
    path("create", views.GameCreateView().as_view(), name="games_list"),
    path("details/<int:pk>", views.GameDetailsView().as_view(), name="game_details"),
    path("update/<int:pk>/", views.GameUpdateView().as_view(), name="game_details"),
    path("make_shot/", views.ShotCreateView().as_view(), name="make_shot"),
]
