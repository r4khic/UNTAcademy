import os

DB_URL = os.environ.get('DB_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres')
DB_TEST_URL = os.environ.get('DB_TEST_URL', 'postgresql+asyncpg://postgres_test:postgres_test@localhost:5433/postgres_test')
