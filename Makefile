.PHONY: build run lock sync

build:
	docker compose build --no-cache

run:
	docker compose up

lock:
	uv pip compile pyproject.toml

sync:
	uv sync
