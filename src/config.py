from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class GeneralSettings(BaseSettings):
    secret_value: Optional[str] = "..."

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

general_settings = GeneralSettings()

class DatabaseSettings(BaseSettings):
    hostname: Optional[str] = "localhost"
    username: Optional[str] = "postgres"
    password: str
    database: Optional[str] = "flip_a_coin"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="db_", extra="allow")

database_settings = DatabaseSettings()

class VaultSettings(BaseSettings):
    addr: Optional[str] = "localhost"
    token: Optional[str] = ""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="vault_", extra="allow")

vault_settings = VaultSettings()

