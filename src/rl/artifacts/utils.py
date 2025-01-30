from src.rl.sqlite_client import SQLiteClient
from src.core.infrastructure.settings import Settings
from src.rl.logger.logger import logger
from pathlib import Path
import mlflow
from sqlalchemy import text


def create_experiment(
    experiment_name: str,
    experiment_dir: Path,
    override: bool = True,
    client: SQLiteClient = SQLiteClient(db_url=Settings().BACKEND_STORE_URI),
) -> str:
    """Helper to create an mlflow experiment. Returns the experiment_id of the created experiment."""

    artifact_dir = experiment_dir / experiment_name
    artifact_dir.mkdir(exist_ok=True, parents=True)

    if (experiment := mlflow.get_experiment_by_name(name=experiment_name)) is None:
        logger.info(event="Creating new experiment", name=experiment)
        return mlflow.create_experiment(
            name=experiment_name,
            artifact_location=str(artifact_dir),
        )
    else:
        logger.info(
            event="Found existing experiment.",
            name=experiment_name,
        )
        if override:
            mlflow.delete_experiment(experiment_id=experiment.experiment_id)
            delete_experiment_by_name(
                client=client,
                experiment_name=experiment_name,
            )
        else:
            raise ValueError("Existing experiment, choose another name.")
        return mlflow.create_experiment(
            name=experiment_name,
            artifact_location=str(artifact_dir),
        )


def delete_experiment_by_name(client: SQLiteClient, experiment_name: str) -> None:
    """Delete an MLflow experiment and all associated data from the SQLite database."""

    experiment_id_query = text("""
    SELECT experiment_id FROM experiments WHERE name = :experiment_name;
    """)
    results = client.query_with_raw_sql(
        experiment_id_query, params={"experiment_name": experiment_name}
    )

    if not results:
        raise ValueError(
            f"Experiment '{experiment_name}' does not exist in the database."
        )

    experiment_id = results[0][0]

    # Delete associated metrics
    delete_metrics_query = text("""
    DELETE FROM metrics
    WHERE run_uuid IN (SELECT run_uuid FROM runs WHERE experiment_id = :experiment_id);
    """)
    client.delete_with_raw_sql(
        delete_metrics_query, params={"experiment_id": experiment_id}
    )

    # Delete associated parameters
    delete_params_query = text("""
    DELETE FROM params
    WHERE run_uuid IN (SELECT run_uuid FROM runs WHERE experiment_id = :experiment_id);
    """)
    client.delete_with_raw_sql(
        delete_params_query, params={"experiment_id": experiment_id}
    )

    # Delete associated tags
    delete_tags_query = text("""
    DELETE FROM tags
    WHERE run_uuid IN (SELECT run_uuid FROM runs WHERE experiment_id = :experiment_id);
    """)
    client.delete_with_raw_sql(
        delete_tags_query, params={"experiment_id": experiment_id}
    )

    delete_runs_query = text(
        """DELETE FROM runs WHERE experiment_id = :experiment_id;"""
    )
    client.delete_with_raw_sql(
        delete_runs_query, params={"experiment_id": experiment_id}
    )

    # Delete the experiment itself
    delete_experiment_query = text(
        """DELETE FROM experiments WHERE experiment_id = :experiment_id;"""
    )
    client.delete_with_raw_sql(
        delete_experiment_query, params={"experiment_id": experiment_id}
    )

    print(
        f"Experiment '{experiment_name}' and all associated data have been deleted successfully."
    )
