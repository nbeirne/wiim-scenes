

deps:
	pip install --no-cache-dir -r requirements.txt

dev:
	flask --app ./app/flask_server.py run --reload

test:
	python3 -m unittest

prod:
	waitress-serve flask_server:app

docker-build:
	docker build -t wiim-scene .

docker-run:
	docker run -p 5000:5000 -e "WIIM_IP_ADDR=$$WIIM_IP_ADDR" wiim-scene

docker-push:
	rm -rf app/__pycache__
	docker buildx build --platform linux/amd64 -t wiim-scene .
	docker tag wiim-scene "192.168.2.10:49153/wiim-scene"
	docker image push "192.168.2.10:49153/wiim-scene"

