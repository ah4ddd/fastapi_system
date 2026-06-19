# centralize evn vars

from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseModel for Environment Variables
"""
basically does:
    database_url
        ↓
    DATABASE_URL

    secret_key
        ↓
    SECRET_KEY

    access_token_expire_minutes
        ↓
    ACCESS_TOKEN_EXPIRE_MINUTES

It converts:
    snake_case
    into
    UPPER_SNAKE_CASE

for environment variable lookup.
"""
class Settings(BaseSettings):
    database_url: str

    jwt_secret_key: str
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    openweather_api_key: str | None = None
    github_token: str | None = None

    coingecko_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

"""
.env
  ↓
Settings class
  ↓
settings object
  ↓
entire application
"""
settings = Settings() # type: ignore

# yet to use
"""
What lru_cache Does — Simple Explanation
lru_cache means "only create the Settings object once, then reuse it forever."
Without it — every time you call get_settings() somewhere in your code,
Python reads the .env file again and creates a new Settings object. Wasteful.
With @lru_cache() — first call creates the Settings object and caches it.
Every subsequent call returns the cached version. One file read, one object, shared everywhere
"""
