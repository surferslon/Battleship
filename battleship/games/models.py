from django.contrib.auth.models import User
from django.db import models
from pyexpat import model


class Game(models.Model):
    winner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="games_won")
    users = models.ManyToManyField(User, related_name="games")


class Ship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()


class ShipDeck(models.Model):
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    killed = models.BooleanField(default=False)
    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="decks")


class Shot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    hit = models.BooleanField(default=False)
