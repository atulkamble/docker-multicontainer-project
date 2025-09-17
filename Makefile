SHELL := /bin/bash
ENV ?= .env

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sort | awk -F':|##' '{printf "\033[36m%-20s\033[0m %s\n", $$1, $$3}'

up: ## Start stack in background
	docker compose --env-file $(ENV) up -d --build
	docker compose ps
	docker compose logs -f --tail=50

down: ## Stop and remove containers (keeps volumes)
	docker compose down

wipe: ## Nuke everything (INCLUDING VOLUMES)
	docker compose down -v --remove-orphans

db: ## Open psql shell
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

ps: ## List containers
	docker compose ps

logs: ## Tail logs
	docker compose logs -f --tail=100
