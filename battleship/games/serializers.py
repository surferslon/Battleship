from games.constants import FIELD_HEIGHT, FIELD_WIDTH
from games.models import Game, Ship, ShipDeck, Shot
from games.utils import GameGenerator, ShotHandler, game_results
from rest_framework import serializers


class ShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shot
        fields = "__all__"
        read_only_fields = ("user",)

    def create(self, validated_data):
        x = validated_data["x"]
        y = validated_data["y"]
        if x not in range(FIELD_WIDTH) or y not in range(FIELD_HEIGHT):
            raise serializers.ValidationError("Coordinates are incorrect")
        user = self.context["request"].user
        game = validated_data["game"]
        shot_handler = ShotHandler(game, user)
        on_target, deck_id = shot_handler.shot(x, y)
        new_shot, _ = Shot.objects.get_or_create(x=x, y=y, game=game, user=user, hit=on_target)
        new_shot.save()
        if on_target:
            game_results(deck_id, game, user)
        return new_shot


class ShipDeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipDeck
        fields = ["x", "y"]


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
        serializer = ShipDeckSerializer(
            instance=ShipDeck.objects.filter(ship__game=self.instance, ship__user=self.context["request"].user),
            many=True,
            context=self.context,
        )
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

    def create(self, validated_data):
        game = Game()
        game.save()
        user = self.context.get("request").user
        game.users.add(user)
        GameGenerator(game).create_ships(user)
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
