.PHONY: discover
SHELL := /bin/bash

isort:
	isort --recursive

flake8:
	flake8 . --ignore=E501 --count --statistics

run-tap:
	@echo "Running Holidays tap.."
	@tap-holidays --config=config/holidays.config.json --catalog=catalog.json
