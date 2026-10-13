from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    twilio_webhook_url: str
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
