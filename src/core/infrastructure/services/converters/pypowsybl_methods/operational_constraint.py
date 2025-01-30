import pandas as pd
from src.core.domain.models.operational_constraint import OperationalConstraint


def list_of_operational_constraint_to_pypowsybl(
    constraints: list[OperationalConstraint],
) -> pd.DataFrame:
    return pd.DataFrame(**constraints)
