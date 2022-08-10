import config
from commands import CommandMapper

if __name__ == "__main__":
    print("\n< BATTLESHIP >")
    print("Use 'help' to get a list of commands\n")
    mapper = CommandMapper()
    while True:
        mapper[input(f"{config.current_user} >>> ")]
