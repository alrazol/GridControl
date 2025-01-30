import typer
from pathlib import Path
from src.core.domain import UseCases
from src.core.infrastructure.adapters import Adapters
from src.core.infrastructure import Configuration
from src.core.infrastructure.settings import Settings

app = typer.Typer()


@app.command()
def compute_simulated_network(
    config_file: Path = typer.Option(..., help="Path to the YAML configuration file."),
    start: str = typer.Option(
        ...,
        help="Simulation start time (e.g., '2024-01-01T00:00:00+0000').",
    ),
    end: str = typer.Option(
        ...,
        help="Simulation end time (e.g., '2024-01-02T00:00:00+0000').",
    ),
    time_step: int = typer.Option(1, help="Time step in hours."),
):
    """
    Run the simulation based on the provided configuration and save the results.
    """

    with Configuration(s=Settings()) as use_cases:
        use_cases.compute_simulated_network(
            config_path=config_file, start=start, end=end, time_step=time_step
        )


if __name__ == "__main__":
    app()
