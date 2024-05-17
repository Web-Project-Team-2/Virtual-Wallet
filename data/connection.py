from mariadb import connect
from mariadb import IntegrityError


def _get_connection(database_name='e_wallet'):
    try:
        conn = connect(
            user='root',
            password='123456',
            host='localhost',
            port=3306,
            database=database_name
        )
        print(f"Connected to the {database_name} database!")
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
