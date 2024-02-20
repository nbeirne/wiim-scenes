

deps:
	pip install --no-cache-dir -r requirements.txt

dev:
	flask --app ./app/flask_server.py run --reload

prod:
	waitress-serve flask_server:app

docker-build:
	docker build -t flask-app .

docker-run:
	docker run -p 5000:5000 -e "WIIM_IP_ADDR=$$WIIM_IP_ADDR" flask-app

