import dotenv
from pathlib import Path
from dotenv import find_dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    DB_URL: str | None = None
    SHOULD_CREATE_TABLES: bool = True
    NETWORK_API_BASEURL: str
    ARTIFACTS_LOCATION: Path
    MLFLOW_TRACKING_URI: str
    LOG_LEVEL: str
