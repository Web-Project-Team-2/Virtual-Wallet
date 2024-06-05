from data.connection import _get_connection_pool


async def read_query(sql: str, sql_params=()):
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, sql_params)
            result = await cursor.fetchall()
            return result


async def insert_query(sql: str, sql_params=()) -> int:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, sql_params)
            await conn.commit()
            return cursor.lastrowid


async def update_query(sql: str, sql_params=()) -> bool:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, sql_params)
            await conn.commit()
            return cursor.rowcount


async def delete_query(sql: str, sql_params=()) -> bool:
    pool = await _get_connection_pool()
    if pool is None:
        raise RuntimeError("Failed to create connection pool")

    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, sql_params)
            await conn.commit()
            return cursor.rowcount > 0