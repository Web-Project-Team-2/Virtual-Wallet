import os
import asyncpg


async def _get_connection_pool():
    try:
        pool = await asyncpg.create_pool(
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '123456'),
            host=os.getenv('DB_HOST', 'postgres'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'e_wallet'),
            min_size=int(os.getenv('DB_MIN_SIZE', 1)),
            max_size=int(os.getenv('DB_MAX_SIZE', 10))
        )
        print("Connection pool created!")
        return pool
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
