import dotenv
from dotenv import find_dotenv
from pydantic_settings import BaseSettings

dotenv.load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    DB_URL: str | None = None
    SHOULD_CREATE_TABLES: bool = True
    NETWORK_API_BASEURL: str
    EXPERIMENTS_DIR: str
    BACKEND_STORE_URI: str
