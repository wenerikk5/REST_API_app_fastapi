freeze:
	pip freeze > requirements.txt

up:
	docker compose up -d --build

down: 
	docker compose down
