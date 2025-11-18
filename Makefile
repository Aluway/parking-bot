.PHONY: install run stop test

install:
	uv sync

run:
	uv run python src/bot.py

stop:
	powershell -ExecutionPolicy Bypass -File stop.ps1

test:
	pytest tests/

