import random

import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from games.constants import FIELD_HEIGHT, FIELD_WIDTH
from games.models import Game, Ship, Shot
from rest_framework import serializers

SHIP_SIZES = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 3,
    "Submarine": 3,
    "Destroyer": 2,
}


class ShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shot
        fields = "__all__"
        read_only_fields = ("user",)

    def build_map(self, game, user):
        field = np.full((FIELD_HEIGHT, FIELD_WIDTH), 0)
        for ship in Ship.objects.filter(game=game).exclude(user=user):
            if ship.orient == "v":
                field[ship.y : ship.y + ship.length, ship.x] = ship.id
            elif ship.orient == "h":
                field[ship.y, ship.x : ship.x + ship.length] = ship.id
        return field

    def ship_is_killed(self, ship, game, user):
        ship_coords = (
            [(ship.x, ship.y + i) for i in range(ship.length)]
            if ship.orient == "v"
            else [(ship.x + i, ship.y) for i in range(ship.length)]
        )
        for coord in ship_coords:
            try:
                Shot.objects.get(x=coord[0], y=coord[1], game=game, user=user)
            except ObjectDoesNotExist:
                return False
        return True

    def count_damage(self, hit, game, user):
        ship = Ship.objects.get(id=hit)
        if self.ship_is_killed(ship, game, user):
            Ship.objects.filter(id=hit).update(killed=True)
        if (
            Ship.objects.filter(game=game, user=ship.user).count()
            == Ship.objects.filter(game=game, user=ship.user, killed=True).count()
        ):
            game.winner = user
            game.save()

    def create(self, validated_data):
        user = self.context["request"].user
        game = validated_data["game"]
        field = self.build_map(game, user)
        if validated_data["x"] not in range(10) or validated_data["y"] not in range(10):
            raise serializers.ValidationError("Coordinates are incorrect")
        hit = field[validated_data["y"], validated_data["x"]]
        new_shot, _ = Shot.objects.get_or_create(
            x=validated_data["x"],
            y=validated_data["y"],
            game=validated_data["game"],
            user=user,
            hit=bool(hit),
        )
        new_shot.save()
        if hit:
            self.count_damage(hit, game, user)
        return new_shot


class ShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ship
        fields = ["x", "y", "length", "orient"]


class GameListSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True)
    winner = serializers.StringRelatedField()

    class Meta:
        model = Game
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
    enemy = serializers.SerializerMethodField()
    ships = serializers.SerializerMethodField()
    shots = serializers.SerializerMethodField()
    turn = serializers.SerializerMethodField()
    winner = serializers.StringRelatedField()

    def get_turn(self, *args, **kwargs):
        user = self.context["request"].user
        if not (last_shot := Shot.objects.filter(game=self.instance).order_by("-id").first()):
            return "<" if self.instance.users.first() == user else ">"
        return (
            "<"
            if ((last_shot.user == user and last_shot.hit) or (last_shot.user != user and not last_shot.hit))
            else ">"
        )

    def get_enemy(self, *args, **kwargs):
        enemy = self.instance.users.exclude(id=self.context["request"].user.id).first()
        return enemy.username if enemy else None

    def get_ships(self, *args, **kwargs):
        ships_queryset = Ship.objects.filter(game=self.instance, user=self.context["request"].user)
        serializer = ShipSerializer(instance=ships_queryset, many=True, context=self.context)
        return serializer.data

    def get_shots(self, *args, **kwargs):
        user = self.context["request"].user
        serializer_player = ShotSerializer(
            instance=Shot.objects.filter(game=self.instance, user=user), many=True, context=self.context
        )
        serializer_enemy = ShotSerializer(
            instance=Shot.objects.filter(game=self.instance).exclude(user=user), many=True, context=self.context
        )
        return {"player": serializer_player.data, "enemy": serializer_enemy.data}

    class Meta:
        model = Game
        fields = ["id", "enemy", "ships", "shots", "turn", "winner"]

    def get_offsets(self, orient, start_point, length):
        start_y, start_x = start_point
        offset_x = start_x - 1 if start_x > 0 else start_x
        offset_y = start_y - 1 if start_y > 0 else start_y
        if orient == "h":
            offset = 3 if start_y > 0 else 2
        elif orient == "v":
            offset = 3 if start_x > 0 else 2
        return offset_y, offset_x, offset, length + 2

    def fill_ship_space(self, field, orient, start_point, length):
        # TODO: exclude used points from points list
        start_y, start_x, offset, length = self.get_offsets(orient, start_point, length)
        for i in range(offset):
            if orient == "v" and 10 > start_x + i > -1:
                field[start_y : start_y + length, start_x + i] = 1
            elif orient == "h" and 10 > start_y + i > -1:
                field[start_y + i, start_x : start_x + length] = 1

    def choose_start_point(self, field, points_list, orient, ship_size):
        coord = random.choice(points_list)
        while any(
            [
                (orient == "v" and 1 in field[coord[0] : coord[0] + ship_size, coord[1]]),
                (orient == "v" and coord[0] + ship_size > 9),
                (orient == "h" and 1 in field[coord[0], coord[1] : coord[1] + ship_size]),
                (orient == "h" and coord[1] + ship_size > 9),
            ]
        ):
            coord = random.choice(points_list)
        return coord[0], coord[1]

    def create_ships(self, current_user, game):
        for user in (current_user, None):
            field = np.full((FIELD_HEIGHT, FIELD_WIDTH), 0)
            points_list = [(ii, i) for ii in range(FIELD_HEIGHT) for i in range(FIELD_WIDTH)]
            for ship_size in SHIP_SIZES.values():
                orient = random.choice(("v", "h"))
                start_point = self.choose_start_point(field, points_list, orient, ship_size)
                self.fill_ship_space(field, orient, start_point, ship_size)
                Ship.objects.create(
                    y=start_point[0], x=start_point[1], length=ship_size, orient=orient, user=user, game=game
                )

    def create(self, validated_data):
        game = Game()
        game.save()
        user = self.context.get("request").user
        game.users.add(user)
        self.create_ships(user, game)
        return game

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user in instance.users.all():
            return instance
        if instance.users.count() > 1:
            raise serializers.ValidationError("Game is already started")
        instance.users.add(user)
        Ship.objects.filter(game=instance, user=None).update(user=user)
        return instance
