from data.database_queries import insert_query, read_query, delete_query, update_query
from data.models.user import User
from pydantic import EmailStr
from schemas.transactions import TransactionFilters
from schemas.user import AdminUserInfo

async def get_all_users(search=None, page=1, size=10):
    sql = "SELECT id, username, email, phone_number, is_admin, create_at, status, balance FROM users"

    where_clauses = []

    if search:
        search_fields = ['phone_number', 'username', 'email']
        search_clauses = [f"{field} LIKE '%{search}%'" for field in search_fields]
        where_clauses.append('(' + ' OR '.join(search_clauses) + ')')

    if where_clauses:
        sql += ' WHERE ' + ' AND '.join(where_clauses)

    offset = (page - 1) * size
    sql += f" LIMIT {size} OFFSET {offset}"

    results = await read_query(sql)
    return [AdminUserInfo.from_query_result(*row) for row in results]

async def block_user(user_id: int):
    return await update_query("UPDATE users SET status = 'blocked' WHERE id = %s", (user_id,))

async def unblock_user(user_id: int):
    return await update_query("UPDATE users SET status = 'activated' WHERE id = %s", (user_id,))

async def approve_user(email: EmailStr):
    return await update_query("UPDATE users SET status = 'activated' WHERE email = %s", (email,))

async def check_if_not_admin(current_user_id: int):
    data = await read_query("SELECT COUNT(*) from users WHERE id = %s AND is_admin = 1", (current_user_id,))
    return data == [(0,)]

async def view_user_transactions(user_id: int, current_user: int, filters: TransactionFilters):
    admin_status = await read_query('SELECT is_admin FROM users WHERE id=%s', (current_user,))
    if not admin_status or not admin_status[0][0]:
        return "Not authorized. Must be an admin"

    query = """
        SELECT status, transaction_date, amount, sender_id, receiver_id, cards_id 
        FROM transactions 
        WHERE (sender_id=%s OR receiver_id=%s)
    """
    params = [user_id, user_id]

    if filters.start_date:
        query += " AND transaction_date >= %s"
        params.append(filters.start_date)
    if filters.end_date:
        query += " AND transaction_date <= %s"
        params.append(filters.end_date)
    if filters.sender_id:
        query += " AND sender_id = %s"
        params.append(filters.sender_id)
    if filters.recipient_id:
        query += " AND receiver_id = %s"
        params.append(filters.recipient_id)
    if filters.direction:
        if filters.direction == 'incoming':
            query += " AND receiver_id = %s"
            params.append(user_id)
        elif filters.direction == 'outgoing':
            query += " AND sender_id = %s"
            params.append(user_id)

    query += f" ORDER BY {filters.sort_by} {filters.sort_order} LIMIT %s OFFSET %s"
    params.extend([filters.limit, filters.offset])

    get_user_data = await read_query(query, params)
    return [
        {
            "status": user_data[0],
            "transaction_date": user_data[1],
            "amount": user_data[2],
            "sender_id": user_data[3],
            "receiver_id": user_data[4],
            "card_id": user_data[5]
        } for user_data in get_user_data
    ]

async def pending_transactions(current_user: int, user_id: int):
    admin_status = await read_query('SELECT is_admin FROM users WHERE id=%s', (current_user,))
    if not admin_status or not admin_status[0][0]:
        return "Not authorized. Must be an admin"

    pending_transactions_data = await read_query("SELECT id, amount FROM transactions WHERE status='pending' AND sender_id=%s", (user_id,))
    if not pending_transactions_data:
        return "There aren't any pending transactions."

    for transaction in pending_transactions_data:
        transaction_id = transaction[0]
        amount = transaction[1]
        await update_query("UPDATE transactions SET status='declined' WHERE id=%s", (transaction_id,))
        await update_query("UPDATE users SET balance=%s WHERE id=%s", (amount, transaction_id,))

    return "All pending transactions have been declined."
