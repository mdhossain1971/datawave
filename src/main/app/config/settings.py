from pydantic_settings import BaseSettings, SettingsConfigDict

# inherits from BaseSettings
class Settings(BaseSettings):
    # Underscores in Python → UPPERCASE with underscores in env var
    # So app_name → APP_NAME
    app_name: str
    app_version: str
    debug: bool = False
    greeting_message: str  = "Default Message"
    database_url: str
    test_database_url: str

    #Inner class
    #This tells Pydantic: "Look in .env file for environment variables."
    #Without this, it would only check system env vars.
    #class Config:
    #    env_file = ".env"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()