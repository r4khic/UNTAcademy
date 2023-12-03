import os

DB_URL = os.environ.get('postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres')
