from pydantic_settings import BaseSettings
from pydantic import SecretStr, EmailStr


class Settings(BaseSettings):
    # server
    BASE_URL: str

    # db
    SQLALCHEMY_DATABASE_URL: str

    # jwt
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # email
    RESEND_API_KEY: SecretStr
    RESEND_SENDER_EMAIL: EmailStr


settings = Settings()
