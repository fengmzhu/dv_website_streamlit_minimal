# DV Management System - Minimal Version Makefile

.PHONY: help setup install run clean

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
	@echo "$(GREEN)Commands:$(NC)"
	@echo "  make setup    - Create venv and install minimal dependencies"
	@echo "  make install  - Install dependencies only"
	@echo "  make run      - Run the minimal application"
	@echo "  make clean    - Clean temporary files"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make setup && make run"

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