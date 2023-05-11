-include .env

# commands
lint:
	echo "Linting"
	isort src
	mypy src
	flake8 src

test:
	echo "Testing"
	pytest

dev.install:
	echo "Download requirements"
	pip install -r requirements.txt
	pip install -r requirements.dev.txt

data.load:
	echo "Download data"
	cd src
	python -m src.load_data

build: dev.install lint test
run:
	echo "Run bot"
	python src.main.py