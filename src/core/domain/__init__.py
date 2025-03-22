from src.core.domain.ports import Ports
from src.core.domain.use_cases.import_network_from_json import ETLPipeline
from src.core.domain.use_cases.compute_simulated_network import SimulationPipeline
from pathlib import Path


class UseCases:
    def __init__(self, p: Ports) -> None:
        self.ports = p

    def import_network_from_json(self, file_path: Path) -> None:
        etl = ETLPipeline(
            network_repository=self.ports.network_repository(),
            network_builder=self.ports.network_builder(),
        )
        etl.run(file_path=file_path)

    def compute_simulated_network(
        self, config_path: Path, start: str, end: str, time_step: int
    ) -> None:  # TODO: Change start and end to datetime
        pipeline = SimulationPipeline(
            config_path=config_path,
            network_repository=self.ports.network_repository(),
            network_builder=self.ports.network_builder(),
        )
        pipeline.apply_pipeline(start=start, end=end, time_step=time_step)
