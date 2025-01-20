# Makefile for Brick Breaker Game

# Variables
PYTHON = python3
SCRIPT = brick_breaker_game.py
VENV_DIR = venv
REQS = requirements.txt

# Default target
.PHONY: run
run: $(VENV_DIR)
	$(VENV_DIR)/bin/$(PYTHON) $(SCRIPT)

# Create virtual environment
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/$(PYTHON) -m pip install --upgrade pip
	$(VENV_DIR)/bin/$(PYTHON) -m pip install -r $(REQS)

default: run

# Install dependencies
.PHONY: install
install: $(VENV_DIR)
	$(VENV_DIR)/bin/$(PYTHON) -m pip install -r $(REQS)

# Clean up
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
