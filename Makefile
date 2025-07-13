# DV Management System - Minimal Version Makefile

.PHONY: help setup install run clean docker-build docker-run docker-stop docker-logs docker-clean organize

# Default target
.DEFAULT_GOAL := help

# Configuration
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
STREAMLIT := $(VENV_DIR)/bin/streamlit
APP_FILE := app.py
PORT := 8501
HOST := 0.0.0.0

# Docker Configuration
DOCKER_IMAGE := dv-website
DOCKER_TAG := latest
DOCKER_CONTAINER := dv-website-container

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m

## Display help information
help:
	@echo "$(BLUE)DV Management System - Minimal Version$(NC)"
	@echo "$(YELLOW)Ultra-lightweight with only 3 dependencies$(NC)"
	@echo ""
	@echo "$(GREEN)Local Development:$(NC)"
	@echo "  make setup       - Create venv and install minimal dependencies"
	@echo "  make install     - Install dependencies only"
	@echo "  make run         - Run the minimal application"
	@echo "  make clean       - Clean temporary files"
	@echo ""
	@echo "$(GREEN)Docker Commands:$(NC)"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with Docker (production-ready)"
	@echo "  make docker-stop  - Stop Docker container"
	@echo "  make docker-logs  - View Docker container logs"
	@echo "  make docker-clean - Remove Docker containers and images"
	@echo ""
	@echo "$(GREEN)Organization:$(NC)"
	@echo "  make organize     - Organize project structure"
	@echo ""
	@echo "$(YELLOW)Quick Start (Local):$(NC) make setup && make run"
	@echo "$(YELLOW)Quick Start (Docker):$(NC) make docker-build && make docker-run"

## Create virtual environment
venv:
	@echo "$(YELLOW)🐍 Creating virtual environment...$(NC)"
	python3 -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ Virtual environment created$(NC)"

## Complete setup
setup: venv
	@echo "$(YELLOW)📦 Installing minimal dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Minimal setup complete!$(NC)"
	@echo "$(BLUE)💡 Only 3 packages installed: streamlit, pandas, openpyxl$(NC)"
	@echo "$(BLUE)💡 To run: make run$(NC)"

## Install dependencies
install:
	@echo "$(YELLOW)📦 Installing minimal dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

## Run the minimal application
run:
	@echo "$(GREEN)🚀 Starting DV Management System (Minimal)...$(NC)"
	@echo "$(BLUE)📊 Access at: http://localhost:$(PORT)$(NC)"
	@echo "$(YELLOW)Ultra-lightweight version with core features only$(NC)"
	$(STREAMLIT) run $(APP_FILE) --server.port $(PORT) --server.address $(HOST)

## Clean temporary files
clean:
	@echo "$(YELLOW)🧹 Cleaning temporary files...$(NC)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -f *.db 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

## Docker Commands ##

## Build Docker image
docker-build:
	@echo "$(YELLOW)🐳 Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✅ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

## Run with Docker (production-ready)
docker-run:
	@echo "$(YELLOW)🚀 Starting DV website with Docker...$(NC)"
	@echo "$(BLUE)📊 Will be available at: http://localhost:$(PORT)$(NC)"
	@echo "$(BLUE)🐳 Container name: $(DOCKER_CONTAINER)$(NC)"
	docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p $(PORT):8501 \
		-v $(shell pwd)/database:/app/database \
		-v $(shell pwd)/exports:/app/exports \
		-v $(shell pwd)/imports:/app/imports \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@sleep 3
	@echo "$(GREEN)✅ Docker container started successfully$(NC)"
	@echo "$(BLUE)💡 Use 'make docker-logs' to view logs$(NC)"
	@echo "$(BLUE)💡 Use 'make docker-stop' to stop the container$(NC)"

## Run with Docker Compose (recommended for production)
docker-compose-up:
	@echo "$(YELLOW)🚀 Starting DV website with Docker Compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Application started with Docker Compose$(NC)"
	@echo "$(BLUE)📊 Available at: http://localhost:$(PORT)$(NC)"

## Stop Docker Compose
docker-compose-down:
	@echo "$(YELLOW)🛑 Stopping Docker Compose services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Docker Compose services stopped$(NC)"

## Stop Docker container
docker-stop:
	@echo "$(YELLOW)🛑 Stopping Docker container...$(NC)"
	-docker stop $(DOCKER_CONTAINER)
	-docker rm $(DOCKER_CONTAINER)
	@echo "$(GREEN)✅ Docker container stopped and removed$(NC)"

## View Docker container logs
docker-logs:
	@echo "$(BLUE)📋 Docker container logs (press Ctrl+C to exit):$(NC)"
	docker logs -f $(DOCKER_CONTAINER)

## Clean Docker containers and images
docker-clean: docker-stop
	@echo "$(YELLOW)🧹 Cleaning Docker containers and images...$(NC)"
	-docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG)
	-docker system prune -f
	@echo "$(GREEN)✅ Docker cleanup complete$(NC)"

## Organization Commands ##

## Organize project structure
organize:
	@echo "$(YELLOW)📁 Organizing project structure...$(NC)"
	@mkdir -p config deployment docs/architecture docs/api exports imports scripts tests
	@echo "$(BLUE)📂 Created directories:$(NC)"
	@echo "  config/          - Configuration files"
	@echo "  deployment/      - Deployment scripts and configs"
	@echo "  docs/architecture/ - Architecture documentation"
	@echo "  docs/api/        - API documentation"
	@echo "  exports/         - Data export files"
	@echo "  imports/         - Data import files"
	@echo "  scripts/         - Utility scripts"
	@echo "  tests/           - Test files"
	@echo "$(GREEN)✅ Project structure organized$(NC)"
	@echo "$(BLUE)💡 Consider moving files to appropriate directories$(NC)"