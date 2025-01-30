include .env

start-mlflow-server:
	@echo "Starting MLflow server..."
	uv run mlflow server --port $(MLFLOW_PORT) --backend-store-uri $(BACKEND_STORE_URI)
