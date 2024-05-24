from data.database_queries import insert_query, read_query, delete_query, update_query
from data.models.user import User
from pydantic import EmailStr



def get_all_users(search=None, page=1, size=10):
    sql = "SELECT id, email, username, phone_number, is_admin, create_at, status, balance FROM users"

    where_clauses = []

    if search:
        search_fields = ['phone_number', 'username', 'email']
        search_clauses = [f"{field} LIKE '%{search}%'" for field in search_fields]
        where_clauses.append('(' + ' OR '.join(search_clauses) + ')')

    if where_clauses:
        sql += ' WHERE ' + ' AND '.join(where_clauses)

    offset = (page - 1) * size
    sql += f" LIMIT {size} OFFSET {offset}"

    return (User.from_query_result(*row) for row in read_query(sql))


def block_user(user_id: int):
    sql = update_query("UPDATE users SET status = 'blocked' WHERE id =?", (user_id,))

    return sql


def unblock_user(user_id: int):
    sql = update_query("UPDATE users SET status = 'activated' WHERE id =?", (user_id,))

    return sql

def approve_user(email: EmailStr):
    sql = update_query("UPDATE users SET status = 'activated' WHERE email = ?", (email,))

    return sql


def check_if_not_admin(current_user_id: int):
    data = read_query("SELECT COUNT(*) from users WHERE id = ? AND is_admin = 1", (current_user_id, ))
    if data == [(0,)]:
        return True

    return False
