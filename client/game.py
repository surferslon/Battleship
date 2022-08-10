import os
import time
from collections.abc import Mapping

import numpy as np
from config import (
    FIELD_HEIGHT,
    FIELD_WIDTH,
    LINE_LENGTH,
    URL_GAME_DETAILS,
    URL_MAKE_SHOT,
)
from utils import api_client


class GameCommands(Mapping):
    break_out = False

    def __len__(self):
        pass

    def __iter__(self):
        pass

    def __getitem__(self, cmd):
        return getattr(self, cmd, None)

    def quit(self, *args, **kwargs):
        print("\nYou've quited the battle")
        self.break_out = True

    def shot(self, *args, **kwargs):
        x = kwargs.get("coords")[0]
        y = kwargs.get("coords")[1]
        api_client.perform_request(URL_MAKE_SHOT, "post", data={"x": x, "y": y, "game": kwargs["id"]})


class Game:
    player = ""
    enemy = ""
    ships = []
    shots = []
    turn = ""
    ready = False
    winner = None
    mutable_objects = ("turn", "shots", "enemy", "winner", "ships")
    commands = GameCommands()

    def __init__(self, id, player):
        self.id = id
        self.player = player

    def _print_elements(self, enemy_field, player_field):
        print(self.enemy.rjust(LINE_LENGTH, "-") if self.enemy else "<Waiting for enemy>".rjust(LINE_LENGTH, "-"))
        print("\n".join([" ".join(ls) for ls in enemy_field]), end="\n")
        print(self.player.rjust(LINE_LENGTH, "-"))
        print("\n".join([" ".join(ls) for ls in player_field]), end="\n")
        print("fire! (x y)" if self.ready else "Waiting")

    def _fill_maps(self, enemy_field, player_field):
        for ship in self.ships:
            if ship["orient"] == "v":
                player_field[ship["y"] : ship["y"] + ship["length"], ship["x"]] = "#"
            if ship["orient"] == "h":
                player_field[ship["y"], ship["x"] : ship["x"] + ship["length"]] = "#"
        for shot in self.shots["player"]:
            enemy_field[shot["y"], shot["x"]] = "X" if shot["hit"] else "*"
        for shot in self.shots["enemy"]:
            player_field[shot["y"], shot["x"]] = "X" if shot["hit"] else "*"

    def _add_grids(self, enemy_field, player_field):
        numbers_list = list(range(FIELD_HEIGHT))
        numbers_list.insert(0, " ")
        player_field = np.insert(player_field, 0, range(FIELD_WIDTH), axis=0)
        player_field = np.insert(player_field, 0, numbers_list, axis=1)
        enemy_field = np.insert(enemy_field, 0, range(FIELD_WIDTH), axis=0)
        enemy_field = np.insert(enemy_field, 0, numbers_list, axis=1)
        return player_field, enemy_field

    def _refresh(self):
        os.system("clear")
        player_field = np.full((FIELD_HEIGHT, FIELD_WIDTH), ".")
        enemy_field = np.full((FIELD_HEIGHT, FIELD_WIDTH), ".")
        self._fill_maps(enemy_field, player_field)
        player_field, enemy_field = self._add_grids(enemy_field, player_field)
        self._print_elements(enemy_field, player_field)

    def _update_game(self, resp):
        resp = resp.json()
        changes = False
        for obj in self.mutable_objects:
            if getattr(self, obj) != resp.get(obj):
                setattr(self, obj, resp.get(obj))
                changes = True
        self.ready = bool(self.enemy) and self.turn == "<" and not self.winner
        if changes:
            self._refresh()

    def _input_command(self):
        cmd = input(">>> ")
        args = {}
        if not (func := self.commands[cmd]):
            coords = cmd.split()
            if len(coords) < 2:
                return
            func = self.commands["shot"]
            args.update({"coords": coords, "id": self.id})
        func(**args)

    def start(self):
        while True:
            self._update_game(api_client.perform_request(f"{URL_GAME_DETAILS}/{self.id}", "get", {}))
            if self.ready:
                self._input_command()
            elif self.winner:
                print(f"\nGame over! The winner is {self.winner}\n")
                break
            else:
                try:
                    time.sleep(3)
                except KeyboardInterrupt:
                    print("\nYou've quited the battle")
                    break
            if self.commands.break_out:
                break
