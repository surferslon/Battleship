from games.models import Game, Shot
from games.serializers import GameListSerializer, GameSerializer, ShotSerializer
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)


class GameListView(ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameListSerializer


class GameCreateView(CreateAPIView):
    model = Game
    serializer_class = GameSerializer


class GameUpdateView(UpdateAPIView):
    model = Game
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class GameDetailsView(RetrieveAPIView):
    model = Game
    serializer_class = GameSerializer
    queryset = Game.objects.all()


class ShotCreateView(CreateAPIView):
    model = Shot
    serializer_class = ShotSerializer
