include .env

start-mlflow-server:
	@echo "Starting MLflow server..."
	uv run mlflow server --port $(MLFLOW_PORT) --backend-store-uri $(MLFLOW_TRACKING_URI)
