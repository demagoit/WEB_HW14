from pydantic_settings import BaseSettings
from pydantic import EmailStr, ConfigDict, field_validator
from fastapi_limiter.depends import RateLimiter

class Route_restrictions():
    def __init__(self):
        self.TIME_SLOT_SECONDS = 5
        self.REQUESTS_PER_TIME_SLOT = 2
        self.rate_limiter = RateLimiter(times=self.REQUESTS_PER_TIME_SLOT,
                    seconds=self.TIME_SLOT_SECONDS)
        self.restict_descr = f'No more than {self.REQUESTS_PER_TIME_SLOT} requests per {self.TIME_SLOT_SECONDS} seconds.'

class Settings(BaseSettings):
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    SECRET_JWT: str
    ALGORITHM_JWT: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DB_URL: str

    REDIS_HOST: str
    REDIS_PORT: int
    # REDIS_PASSWORD: str | None

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str


    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8')

    @field_validator('ALGORITHM_JWT')
    def validate_algo(cls, value):
        accepted = ['HS256', 'HS512']
        if value not in accepted:
            raise ValueError(f'Accepted algorithms are: {accepted}')
        return value

config = Settings()
route_rst = Route_restrictions()
