# Battleship

## Requirements
- Docker
- Poetry (https://python-poetry.org/docs/#installation)

## Description
Once the project is cloned use the following makefile commands to run the app and it the client<br>
Optionally you can use the `requirements.txt` to create a clinet environment. To run the client use `python client/main.py`.

- `make init` <br>
Build the image with the server and setup virtual environment for the client
- `make run_server` <br>
Start the server container. The app listens on port 8000.
- `make stop_server` <br>
Stop the server container
- `make run_client` <br>
Run the clinet. Use 'help' command in the client for available commands.
- `make help` <br>
List available makefile commands
