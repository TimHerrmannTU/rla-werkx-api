from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_NAME: str

    OLD_DB_NAME: str
        
    def DATABASE_URL(self, fetch_from_legacy_table = False) -> str:
        table = self.OLD_DB_NAME if fetch_from_legacy_table else self.DB_NAME
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{table}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()