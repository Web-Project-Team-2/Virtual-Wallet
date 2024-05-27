import aiomysql

async def _get_connection_pool():
    try:
        pool = await aiomysql.create_pool(
            user='root',
            password='123456',
            host='db',
            port=3306,
            db='e_wallet',
            minsize=1,
            maxsize=10
        )
        print("Connection pool created!")
        return pool
    except Exception as e:
        print(f"An error occurred: {e}")
        return None