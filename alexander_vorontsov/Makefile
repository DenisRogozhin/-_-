-include .env

# commands
lint:
	echo "Linting"
	isort src
	pydocstyle src
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
	python -m src.load_data

data.preprocessing:
	echo "Preprocessing data"
	python -m src.preprocessing

dev.run: dev.install data.load data.preprocessing lint test
	echo "Run build"
	python src.main.py
fast.run: dev.install
	echo "Run bot"
	python src.main.py