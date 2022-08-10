from abc import ABC, abstractmethod
from collections.abc import Mapping

import config
from config import (
    URL_GAME_DETAILS,
    URL_GAME_UPDATE,
    URL_GAMES_LIST,
    URL_LOGIN,
    URL_NEW_GAME,
    URL_SIGNUP,
)
from game import Game
from utils import api_client


class Command(ABC):
    @abstractmethod
    def perform_command(self):
        pass

    @abstractmethod
    def help():
        pass


class CmdLogin(Command):
    def perform_command(self):
        name = input("Enter your name: ")
        pswd = input("Enter your password: ")
        if api_client.perform_request(URL_LOGIN, "post", {"username": name, "password": pswd}):
            config.current_user = name

    @staticmethod
    def help():
        return "Login with your credentials"


class CmdSignup(Command):
    def perform_command(self):
        name = input("Enter your name: ")
        pswd = input("Enter your password: ")
        resp = api_client.perform_request(URL_SIGNUP, "post", {"username": name, "password": pswd})
        if resp and resp.cookies.get("sessionid"):
            config.current_user = name

    @staticmethod
    def help():
        return "Create a new user"


class CmdHelp(Command):
    def perform_command(self):
        for command, func in CommandMapper.cmd_mapping.items():
            print(f"{command.ljust(10, '.')}{func.help().rjust(30, '.')}")

    @staticmethod
    def help():
        return "Show help"


class CmdGamesList(Command):
    def perform_command(self):
        if not (resp := api_client.perform_request(URL_GAMES_LIST, "get", {})):
            return
        for game in resp.json():
            print(
                str(game["id"]).ljust(5, " "),
                game["users"],
                f"Winner: {game['winner']}" if game["winner"] else "In progress",
            )

    def help():
        return "Get games list"


class CmdNewGame(Command):
    def perform_command(self):
        if not (resp := api_client.perform_request(URL_NEW_GAME, "post", {})):
            return
        resp = resp.json()
        game = Game(id=resp.get("id"), player=config.current_user)
        game.start()

    def help():
        return "Start a new game"


class CmdJoinGame(Command):
    def perform_command(self):
        if not (game_id := input("Game id: ")):
            return
        try:
            int(game_id)
        except ValueError:
            print("Wrong game id")
            return
        if not (resp := api_client.perform_request(f"{URL_GAME_UPDATE}/{game_id}/", "patch", {})):
            return
        resp = resp.json()
        game = Game(id=resp.get("id"), player=config.current_user)
        game.start()

    def help():
        return "Join existing game"


class CmdQuit(Command):
    def perform_command(self):
        exit()

    @staticmethod
    def help():
        return "Quit"


class CommandMapper(Mapping):
    cmd_mapping = {
        "help": CmdHelp,
        "signup": CmdSignup,
        "login": CmdLogin,
        "new": CmdNewGame,
        "games": CmdGamesList,
        "join": CmdJoinGame,
        "quit": CmdQuit,
    }

    def __len__(self):
        return len(self.cmd_mapping)

    def __getitem__(self, cmd):
        try:
            self.cmd_mapping[cmd]().perform_command()
        except KeyError:
            print("Huh?")

    def __iter__(self):
        return iter(self.cmd_mapping)
