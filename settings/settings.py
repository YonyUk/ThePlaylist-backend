import dotenv
import os
import json
from passlib.context import CryptContext
from typing import List

dotenv.load_dotenv()

class Settings:

    _instance = None

    def __init__(self):
        self._db_engine:str = os.getenv('DB_ENGINE','database engine')
        self._db_user:str = os.getenv('DB_USER','database user')
        self._db_host:str = os.getenv('DB_HOST','database host')
        self._db_port:int = int(os.getenv('DB_PORT','listener port for the database'))
        self._db_password:str = os.getenv('DB_PASSWORD','database password')
        self._db_name:str = os.getenv('DB_NAME','database name')
        self._global_api_prefix:str = os.getenv('API_GLOBAL_PREFIX','global api prefix for endpoints')
        self._api_version:str = os.getenv('VERSION','api version')
        self._secret_key:str = os.getenv('SECRET_KEY','your secret key')
        self._algorithm:str = os.getenv('ALGORITHM','algorithm to use')
        self._token_life_time:int = int(os.getenv('ACCESS_TOKEN_EXPIRES_MINUTES','access token life time'))
        self._alembic_config_file_path:str = os.getenv('ALEMBIC_CONFIG_FILE','alembic config file path')
        self._crypt_context:CryptContext = CryptContext(schemes=['bcrypt'],deprecated='auto')
        self._sqlalchemy_pool_size:int = int(os.getenv('SQLALCHEMY_POOL_SIZE','pool size for sqlalchemy'))
        self._sqlalchemy_max_overflow:int = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW','max overflow allowed for sqlalchemy'))
        self._sqlalchemy_pool_timeout:int = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT','pool timeout for sqlalchemy'))
        self._min_username_length:int = int(os.getenv('MIN_USERNAME_LENGTH','minimun length for username'))
        self._min_user_password_length:int = int(os.getenv('MIN_USER_PASSWORD_LENGTH','minimun length for password'))
        self._max_username_length:int = int(os.getenv('MAX_USERNAME_LENGTH','maximun length for username'))
        self._max_user_password_length:int = int(os.getenv('MAX_USER_PASSWORD_LENGTH','maximun length for password'))
        self._page_size:int = int(os.getenv('PAGE_SIZE','size of pages in pagination'))
        self._allowed_origins:List[str] = json.loads(os.getenv('ALLOWED_ORIGINS','origins allowed to make requests to this api'))
        self._allow_credentials:bool = bool(os.getenv('ALLOW_CREDENTIALS','allow credentials sending'))
        self._allowed_methods:List[str] = json.loads(os.getenv('ALLOWED_METHODS','methods allowed from others origins'))

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Settings()
        return cls._instance

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        return self._allowed_origins
    
    @property
    def ALLOW_CREDENTIALS(self) -> bool:
        return self._allow_credentials
    
    @property
    def ALLOWED_METHODS(self) -> List[str]:
        return self._allowed_methods

    @property
    def PAGE_SIZE(self) -> int:
        '''
        size of pages in pagination
        '''
        return self._page_size

    @property
    def MIN_USERNAME_LENGTH(self) -> int:
        '''
        minimun length for username
        '''
        return self._min_username_length
    
    @property
    def MAX_USERNAME_LENGTH(self) -> int:
        '''
        maximun length for username
        '''
        return self._max_username_length
    
    @property
    def MIN_USER_PASSWORD_LENGTH(self) -> int:
        '''
        minimun length for user password
        '''
        return self._min_user_password_length
    
    @property
    def MAX_USER_PASSWORD_LENGTH(self) -> int:
        '''
        maximun length for user password
        '''
        return self._max_user_password_length

    @property
    def SQLALCHEMY_POOL_SIZE(self) -> int:
        '''
        pool size for sqlalchemy
        '''
        return self._sqlalchemy_pool_size

    @property
    def SQLALCHEMY_MAX_OVERFLOW(self) -> int:
        '''
        max overflow allowed for sqlalchemy
        '''
        return self._sqlalchemy_max_overflow
    
    @property
    def SQLALCHEMY_POOL_TIMEOUT(self) -> int:
        '''
        pool timeout for sqlalchemy
        '''
        return self._sqlalchemy_pool_timeout

    @property
    def CRYPT_CONTEXT(self) -> CryptContext:
        '''
        return the global cryptography context
        '''
        return self._crypt_context

    @property
    def DB_ENGINE(self) -> str:
        '''
        database engine currently used
        '''
        return self._db_engine
    
    @property
    def DB_USER(self) -> str:
        '''
        current database host user
        '''
        return self._db_user
    
    @property
    def DB_HOST(self) -> str:
        '''
        database host url
        '''
        return self._db_host
    
    @property
    def DB_PORT(self) -> int:
        '''
        database host listener port 
        '''
        return self._db_port
    
    @property
    def DB_PASSWORD(self) -> str:
        '''
        current user's password in for the database host
        '''
        return self._db_password

    @property
    def DB_NAME(self) -> str:
        '''
        database name
        '''
        return self._db_name

    @property
    def DB_URL(self) -> str:
        '''
        database url
        '''
        return f'{self._db_user}:{self._db_password}@{self._db_host}:{self._db_port}/{self._db_name}'
    
    @property
    def GLOBAL_API_PREFIX(self) -> str:
        '''
        global api prefix for endpoints
        '''
        return self._global_api_prefix
    
    @property
    def API_VERSION(self) -> str:
        '''
        API Version
        '''
        return self._api_version
    
    @property
    def SECRET_KEY(self) -> str:
        '''
        Secret key
        '''
        return self._secret_key
    
    @property
    def ALGORITHM(self) -> str:
        '''
        Algorithm for the OAuth section
        '''
        return self._algorithm
    
    @property
    def TOKEN_LIFE_TIME(self) -> int:
        '''
        authorization token life time
        '''
        return self._token_life_time
    
    @property
    def ALEMBIC_CONFIG_FILE_PATH(self) -> str:
        '''
        config file path for alembic
        '''
        return self._alembic_config_file_path