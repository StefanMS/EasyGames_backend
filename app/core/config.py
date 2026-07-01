'''
Config module
'''
# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Settings(BaseSettings):
    '''
    Class for db settings
    '''
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    ADMIN_USER_EMAIL: str = os.getenv('ADMIN_USER_EMAIL')
    ADMIN_USER_PASSWORD: str = os.getenv('ADMIN_USER_PASSWORD')
    ADMIN_USER_FIRST_NAME: str = os.getenv('ADMIN_USER_FIRST_NAME')
    ADMIN_USER_LAST_NAME: str = os.getenv('ADMIN_USER_LAST_NAME')

    BUCKET_URL: str = os.getenv('BUCKET_URL')
    API_URL: str = os.getenv('API_URL')
    class Config:
        env_file = ".env"


settings = Settings()
