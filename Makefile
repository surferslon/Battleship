project_name := battleship

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init:  ## Start the app
	docker build -t ${project_name} battleship
	docker build -t ${project_name}_client client

run_server:  ## start the server
	docker run --rm -d -p 8000:8000 --name ${project_name} ${project_name}

stop_server:  ## Stop the app
	docker stop ${project_name}

run_client:  ## run the clinet
	docker run --network=host --rm -it --name ${project_name}_client ${project_name}_client
