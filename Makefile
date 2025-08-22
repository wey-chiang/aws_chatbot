.PHONY: help install install-dev setup clean run lint format venv activate

PYTHON := python3
VENV := venv
BIN := $(VENV)/bin
PYTHON_VENV := $(BIN)/python
PIP := $(BIN)/pip

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

venv: ## Create virtual environment
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at ./$(VENV)"
	@echo "Run 'source $(VENV)/bin/activate' to activate it"

install: venv ## Install the package and dependencies
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r requirements.txt
	@echo "Installing aws-chatbot package..."
	@$(PIP) install -e .
	@echo "Installation complete!"

install-dev: venv ## Install package with development dependencies
	@echo "Installing dependencies..."
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -r requirements.txt
	@$(PIP) install -r requirements-dev.txt 2>/dev/null || true
	@echo "Installing aws-chatbot package in development mode..."
	@$(PIP) install -e .
	@echo "Development installation complete!"

setup: install ## Complete setup including .env file
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo "Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo ".env file already exists"; \
	fi
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "1. Activate the virtual environment: source $(VENV)/bin/activate"
	@echo "2. Edit .env file with your OPENAI_API_KEY"
	@echo "3. Configure AWS credentials (aws configure)"
	@echo "4. Run the chatbot: aws-chatbot or python -m aws_chatbot.main"

clean: ## Clean up build artifacts and virtual environment
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf build dist *.egg-info
	@rm -rf **/__pycache__ **/*.pyc
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

run: ## Run the chatbot in interactive mode
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Starting AWS Chatbot..."
	@$(PYTHON_VENV) -m aws_chatbot.main

run-verbose: ## Run the chatbot with verbose output
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Starting AWS Chatbot (verbose mode)..."
	@$(PYTHON_VENV) -m aws_chatbot.main --verbose

query: ## Run a single query (usage: make query Q="your question")
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@if [ -z "$(Q)" ]; then \
		echo "Please provide a query: make query Q=\"your question\""; \
	else \
		$(PYTHON_VENV) -m aws_chatbot.main "$(Q)"; \
	fi

lint: ## Run code linting
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Running linter..."
	@$(PYTHON_VENV) -m flake8 aws_chatbot/ 2>/dev/null || echo "flake8 not installed, skipping..."
	@$(PYTHON_VENV) -m pylint aws_chatbot/ 2>/dev/null || echo "pylint not installed, skipping..."

format: ## Format code with black
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running 'make install' first..."; \
		$(MAKE) install; \
	fi
	@echo "Formatting code..."
	@$(PYTHON_VENV) -m black aws_chatbot/ 2>/dev/null || echo "black not installed, run: pip install black"

test: ## Run tests
	@if [ ! -d "$(VENV)" ]; then \
			echo "Virtual environment not found. Running 'make install' first..."; \
			$(MAKE) install; \
	fi
	@echo "Running tests..."
	@$(PYTHON_VENV) -m pytest tests/

check-aws: ## Check AWS credentials configuration
	@echo "Checking AWS configuration..."
	@aws sts get-caller-identity >/dev/null 2>&1 && \
		echo "✓ AWS credentials are configured" || \
		echo "✗ AWS credentials not configured. Run 'aws configure'"

check-env: ## Check environment variables
	@echo "Checking environment..."
	@if [ -f .env ]; then \
		echo "✓ .env file exists"; \
		grep -q "OPENAI_API_KEY=" .env && \
			echo "✓ OPENAI_API_KEY is set in .env" || \
			echo "✗ OPENAI_API_KEY not set in .env"; \
	else \
		echo "✗ .env file not found. Run 'make setup'"; \
	fi

status: check-env check-aws ## Check full system status
	@echo ""
	@echo "System status check complete!"

# Development shortcuts
dev: install-dev ## Alias for install-dev
build: install ## Alias for install
rebuild: clean install ## Clean and reinstall everything