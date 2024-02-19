

dev:
	flask --app ./flask_server.py run --reload

prod:
	waitress-serve flask_server:app

