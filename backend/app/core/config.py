from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # mysql+pymysql://user:password@127.0.0.1:3306/genai_edu?charset=utf8mb4
    DATABASE_URL: str = 'mysql+pymysql://root:root@127.0.0.1:3307/genai_edu?charset=utf8mb4'

    JWT_SECRET_KEY: str = 'CHANGE_ME_TO_A_LONG_RANDOM_SECRET'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    STORAGE_DIR: str = './storage'

    # LLM configs (must be provided in runtime env or .env)
    ZHIPU_API_KEY: str = 'd52ae79380774b8288dde5311daf6294.Qe4gbpQrmOWtoEx9'
    ZHIPU_MODEL: str = 'glm-4-plus'


settings = Settings()