from pathlib import Path
import typer
from src.core.infrastructure import Configuration
from src.core.infrastructure.settings import Settings

app = typer.Typer()


@app.command()
def import_network_from_json(
    json_paths: list[Path] = typer.Option(
        ..., help="List of paths to the grids to insert"
    ),
):
    """
    Run a ETL process for list of json files.
    """

    with Configuration(s=Settings()) as use_cases:
        for p in json_paths:
            use_cases.import_network_from_json(file_path=p)


if __name__ == "__main__":
    app()
