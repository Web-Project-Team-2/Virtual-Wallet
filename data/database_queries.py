from data.connection import _get_connection_pool


async def read_query(sql: str, sql_params=()):
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        result = await conn.fetch(sql, *sql_params)
        return result


async def insert_query(sql: str, sql_params=()) -> int:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        result = await conn.fetchrow(sql, *sql_params)
        return result['id'] if result and 'id' in result else None


async def update_query(sql: str, sql_params=()) -> bool:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        result = await conn.execute(sql, *sql_params)
        return result


async def delete_query(sql: str, sql_params=()) -> bool:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        result = await conn.execute(sql, *sql_params)
        return result == "DELETE 1"
