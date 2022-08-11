import random

import numpy as np
from games.constants import FIELD_HEIGHT, FIELD_WIDTH
from games.models import Ship, ShipDeck


def game_results(deck_id, game, user):
    if not (
        ShipDeck.objects.filter(
            ship__game=game,
            ship__user=ShipDeck.objects.get(id=deck_id).ship.user,
            killed=False,
        ).count()
    ):
        game.winner = user
        game.save()


class GameGenerator:
    SHIP_SIZES = {
        "Carrier": 5,
        "Battleship": 4,
        "Cruiser": 3,
        "Submarine": 3,
        "Destroyer": 2,
    }

    def __init__(self, game):
        self.game = game

    def _get_offsets(self, orient, start_point, length):
        start_y, start_x = start_point
        offset_x = start_x - 1 if start_x > 0 else start_x
        offset_y = start_y - 1 if start_y > 0 else start_y
        if orient == "h":
            offset = 3 if start_y > 0 else 2
        elif orient == "v":
            offset = 3 if start_x > 0 else 2
        return offset_y, offset_x, offset, length + 2

    def _fill_ship_space(self, orient, start_point, length):
        # TODO: exclude used points from points list
        start_y, start_x, offset, length = self._get_offsets(orient, start_point, length)
        for i in range(offset):
            if orient == "v" and FIELD_WIDTH > start_x + i > -1:
                self.field[start_y : start_y + length, start_x + i] = 1
            elif orient == "h" and FIELD_HEIGHT > start_y + i > -1:
                self.field[start_y + i, start_x : start_x + length] = 1

    def _choose_start_point(self, points_list, orient, ship_size):
        coord = random.choice(points_list)
        while any(
            [
                (orient == "v" and 1 in self.field[coord[0] : coord[0] + ship_size, coord[1]]),
                (orient == "v" and coord[0] + ship_size > 9),
                (orient == "h" and 1 in self.field[coord[0], coord[1] : coord[1] + ship_size]),
                (orient == "h" and coord[1] + ship_size > 9),
            ]
        ):
            coord = random.choice(points_list)
        return coord[0], coord[1]

    def _create_ship_decks(self, ship, start_point, ship_size, orient):
        decks_coords = (
            [(start_point[1], start_point[0] + i) for i in range(ship_size)]
            if orient == "v"
            else [(start_point[1] + i, start_point[0]) for i in range(ship_size)]
        )
        ShipDeck.objects.bulk_create([ShipDeck(x=deck[1], y=deck[0], ship=ship) for deck in decks_coords])

    def create_ships(self, current_user):
        for user in (current_user, None):
            self.field = np.full((FIELD_HEIGHT, FIELD_WIDTH), 0)
            points_list = [(ii, i) for ii in range(FIELD_HEIGHT) for i in range(FIELD_WIDTH)]
            for ship_size in self.SHIP_SIZES.values():
                orient = random.choice(("v", "h"))
                start_point = self._choose_start_point(points_list, orient, ship_size)
                self._fill_ship_space(orient, start_point, ship_size)
                new_ship = Ship.objects.create(y=start_point[0], x=start_point[1], user=user, game=self.game)
                self._create_ship_decks(new_ship, start_point, ship_size, orient)


class ShotHandler:
    def __init__(self, game, user):
        self.game = game
        self.user = user
        self.field = np.full((FIELD_HEIGHT, FIELD_WIDTH), None)
        self._fill_map()

    def _fill_map(self):
        for deck in ShipDeck.objects.filter(ship__game=self.game).exclude(ship__user=self.user):
            self.field[deck.y, deck.x] = deck.id

    def shot(self, x, y):
        deck_id = self.field[y, x]
        if deck_id:
            ShipDeck.objects.filter(id=deck_id).update(killed=True)
        return bool(deck_id), deck_id
