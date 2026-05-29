.PHONY: install test run docker hardhat-test

install:
	python -m pip install -r backend/requirements.txt

test:
	python -m pytest -q

run:
	cd backend && python app.py

docker:
	docker compose up --build

hardhat-test:
	cd hardhat && npm install && npm test
