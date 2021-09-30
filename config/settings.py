from os import environ
from sqlalchemy import create_engine

settings = {
    'skillstreets_db': environ['skillstreets_db'],
    'sendgrid_api_key': environ['sendgrid_api_key'],
    'keycloak_db': environ['keycloak_db']
}

skillstreets_engine = create_engine(
    settings['skillstreets_db'],
    pool_recycle=2,
    pool_use_lifo=True,
    pool_size=2,
    max_overflow=0
)


keycloak_engine = create_engine(
    settings['keycloak_db'],
    pool_recycle=2,
    pool_use_lifo=True,
    pool_size=2,
    max_overflow=0
)