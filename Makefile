## options
# based on https://tech.davis-hansson.com/p/make/
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

## variables

ENVIRONMENT ?= dev
ARGS =
APP_NAME = $(shell python -m src.config app_name)
SOURCE_DIR := src
TEST_DIR := tests

IMAGE_HOST = $(shell python -m src.config image_host)
IMAGE_REPO = $(shell python -m src.config image_repo)
IMAGE_NAME = $(IMAGE_HOST)/$(IMAGE_REPO)/$(APP_NAME)
IMAGE_TAG ?= latest

DIST_DIR := dist
CONDA_ENV_DIR = $(CONDA_PREFIX)

ifeq ($(CONDA_ENV_DIR),)
    CONDA_ENV_DIR := $(shell python -c "import sys; print(sys.prefix)")
endif

## formula

# based on https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:  ## print help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## dependencies

.PHONY: deps-install
deps-install:  ## install dependencies
	poetry install
	python -m pre_commit install --install-hooks

.PHONY: deps-install-ci
deps-install-ci:  ## install CI
	python -m pip install poetry
	python -m poetry config virtualenvs.create false
	python -m poetry install --no-root
	python -m poetry show

.PHONY: deps-update
deps-update:  ## update dependencies
	poetry update
	poetry export --format requirements.txt --output requirements.txt --without-hashes
	python -m pre_commit autoupdate

requirements.txt: poetry.lock ## export requirements.txt
	poetry export --format requirements.txt --output requirements.txt --without-hashes

requirements-dev.txt: poetry.lock  ## export requirements-dev.txt
	poetry export --with dev --format requirements.txt --output requirements-dev.txt --without-hashes

## checks

.PHONY: format
format: ## format code
	python -m ruff check --fix .  # 使用 ruff 进行代码规范检查并尝试自动修复
	python -m isort .   # 使用 isort 对 import 语句进行排序
	python -m black $(SOURCE_DIR) $(TEST_DIR)  # 使用 black 对代码进行格式化

.PHONY: lint
lint: ## static code check
	python -m ruff check .  # 使用 ruff 进行代码规范检查
	python -m isort . --check --diff   # 使用 isort 检查 import 语句是否按规则排序，并显示差异
	python -m black $(SOURCE_DIR) $(TEST_DIR) --diff  # 使用 black 检查代码格式，并显示差异
	python -m mypy $(SOURCE_DIR)  # 使用 mypy 进行静态类型检查

.PHONY: test
test:  ## code test
	python -m pytest $(TEST_DIR) --cov $(SOURCE_DIR)

.PHONY: run-ci
run-ci: deps-install-ci lint test  ## run ci

## app

.PHONY: run-task
run-task:  ## run python task
	python -m src.task

# Add a new target for building the Typer app as an exe
.PHONY: build-task-exe
build-task-exe:  ## build task exe
	$(CONDA_ENV_DIR)/bin/pyinstaller -F --distpath $(DIST_DIR) --name task $(SOURCE_DIR)/task.py # 修改 build-exe 目标，使用已存在的 conda 环境

.PHONY: run-web-dev
run-web-dev:  ## run web app dev
	python -m uvicorn src.web:app --reload

.PHONY: run-web
run-web:  ## run python web
	python -m gunicorn src.web:app -c src/gunicorn_conf.py

.PHONY: run
run: run-web  ## run main python app

## docker-compose

.PHONY: dc-build
dc-build: requirements.txt  ## build web_dev、web_ci、web image
	IMAGE_TAG=$(IMAGE_TAG) docker compose build web_dev web_ci web # 使用 Docker Compose 构建名为 web_dev、web_ci、web 的服务镜像

.PHONY: dc-push
dc-push: ## push web_dev and web docker image
	IMAGE_TAG=$(IMAGE_TAG) docker compose push web_dev web # 使用 Docker Compose 推送名为 web_dev 和 web 的服务镜像

.PHONY: dc-test
dc-ci: ## run web_ci, end delete
	docker compose run --rm web_ci # 使用 Docker Compose 运行名为 web_ci 的服务容器，--rm 选项表示容器运行结束后立即删除容器

.PHONY: dc-up
dc-up:  ## run web dev app image
	docker compose up web_dev # 使用 Docker Compose 启动名为 web_dev 的服务容器

.PHONY: dc-exec
dc-exec: ## run web_dev exec /bin/bash
	docker compose exec web_dev /bin/bash # 使用 Docker Compose 在 web_dev 服务容器中执行交互式的 Bash shell

.PHONY: dc-stop
dc-stop: ## stop docker server
	docker compose stop # 使用 Docker Compose 停止正在运行的服务容器

.PHONY: dc-down
dc-down: ## stop and delete docker server
	docker compose down  ## 停止并删除正在运行的 Docker 服务容器及其网络
