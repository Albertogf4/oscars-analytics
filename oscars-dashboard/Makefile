.PHONY: dev backend frontend stop stop-backend stop-frontend restart install install-backend install-frontend clean clear-cache help

# Default target - run both backend and frontend
dev: stop
	@echo "Starting Oscar Dashboard..."
	@make -j2 backend frontend

# Run backend only
backend:
	@echo "Starting backend on http://localhost:8000"
	cd backend && python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Run frontend only
frontend:
	@echo "Starting frontend on http://localhost:5173"
	cd frontend && npm run dev

# Stop all services
stop: stop-backend stop-frontend
	@echo "All services stopped."

# Stop backend (kill process on port 8000)
stop-backend:
	@echo "Stopping backend..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Stop frontend (kill process on port 5173)
stop-frontend:
	@echo "Stopping frontend..."
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Restart all services
restart: stop dev

# Install all dependencies
install: install-backend install-frontend
	@echo "All dependencies installed!"

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip3 install -r requirements.txt

# Install frontend dependencies
install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf frontend/node_modules frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Clear backend cache
clear-cache:
	@echo "Clearing backend cache..."
	rm -rf backend/cache/*.json
	@echo "Cache cleared."

# Show help
help:
	@echo "Oscar Dashboard - Available commands:"
	@echo ""
	@echo "  make dev              - Stop existing & run both services (default)"
	@echo "  make backend          - Run backend only (port 8000)"
	@echo "  make frontend         - Run frontend only (port 5173)"
	@echo "  make stop             - Stop all running services"
	@echo "  make stop-backend     - Stop backend only"
	@echo "  make stop-frontend    - Stop frontend only"
	@echo "  make restart          - Restart all services"
	@echo "  make install          - Install all dependencies"
	@echo "  make install-backend  - Install Python dependencies"
	@echo "  make install-frontend - Install Node dependencies"
	@echo "  make clean            - Remove build artifacts"
	@echo "  make clear-cache      - Clear Kalshi API cache"
	@echo "  make help             - Show this help message"
