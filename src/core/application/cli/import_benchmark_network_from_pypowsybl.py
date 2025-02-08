import typer
from typing import Literal
from src.core.infrastructure import Configuration
from src.core.infrastructure.settings import Settings

app = typer.Typer()


@app.command()
def import_benchmark_network_from_pypowsybl(
    network_name: Literal["ieee14"] = typer.Option(
        ..., help="Name of the benchmark network to load."
    ),
):
    """
    Run a ETL process for list of json files.
    """

    with Configuration(s=Settings()) as use_cases:
        use_cases.import_benchmark_network_from_pypowsybl(network_name=network_name)


if __name__ == "__main__":
    app()
