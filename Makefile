.PHONY: install run test

install:
	uv sync

run:
	python src/bot.py

test:
	pytest tests/

