.PHONY: help install run test studio docker-build docker-up docker-down docker-logs docker-shell docker-studio-logs clean

PORT ?= 8000
LANGGRAPH_PORT ?= 2024
COMPOSE ?= docker compose

help:
	@echo "Targets disponiveis:"
	@echo "  make install            - instala dependencias com Poetry"
	@echo "  make run                - sobe a API local (uvicorn --reload)"
	@echo "  make test               - roda os testes"
	@echo "  make studio             - sobe o LangGraph Studio local"
	@echo "  make docker-build       - build da imagem Docker"
	@echo "  make docker-up          - sobe API + LangGraph Dev (Docker)"
	@echo "  make docker-down        - para os containers"
	@echo "  make docker-logs        - acompanha logs (api + studio)"
	@echo "  make docker-studio-logs - acompanha logs do LangGraph Dev"
	@echo "  make docker-shell       - abre shell no container da API"
	@echo "  make clean              - remove caches locais"

install:
	poetry install

run:
	PYTHONPATH=. poetry run uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

test:
	PYTHONPATH=. poetry run pytest -q

studio:
	@echo ""
	@echo "LangGraph Dev API:  http://127.0.0.1:$(LANGGRAPH_PORT)"
	@echo "LangGraph Studio:   https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:$(LANGGRAPH_PORT)"
	@echo "API Docs:           http://127.0.0.1:$(LANGGRAPH_PORT)/docs"
	@echo ""
	poetry run langgraph dev --host 0.0.0.0 --port $(LANGGRAPH_PORT)

docker-build:
	$(COMPOSE) build

docker-up:
	$(COMPOSE) up --build -d
	@echo ""
	@echo "API:                http://127.0.0.1:$(PORT)/docs"
	@echo "LangGraph Dev API:  http://127.0.0.1:$(LANGGRAPH_PORT)"
	@echo "LangGraph Studio:   https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:$(LANGGRAPH_PORT)"
	@echo ""

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f api studio

docker-studio-logs:
	$(COMPOSE) logs -f studio

docker-shell:
	$(COMPOSE) exec api sh

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .ruff_cache .coverage htmlcov
