from typing import Optional

from data.database_queries import insert_query, read_query, delete_query, update_query
from data.models.user import User
from pydantic import EmailStr
from schemas.transactions import TransactionFilters
from schemas.user import AdminUserInfo

async def get_all_users(search: Optional[str] = None, page: int = 1, size: int = 10) -> list[AdminUserInfo]:
    sql = "SELECT id, username, email, phone_number, is_admin, create_at, status, balance FROM users"

    where_clauses = []

    if search:
        search_fields = ['phone_number', 'username', 'email']
        search_clauses = [f"{field} LIKE $1" for field in search_fields]
        where_clauses.append('(' + ' OR '.join(search_clauses) + ')')

    if where_clauses:
        sql += ' WHERE ' + ' AND '.join(where_clauses)

    offset = (page - 1) * size
    sql += f" LIMIT $2 OFFSET $3"

    results = await read_query(sql, [f'%{search}%', size, offset])
    return [AdminUserInfo.from_query_result(*row) for row in results]

async def block_user(user_id: int) -> bool:
    return await update_query("UPDATE users SET status = 'blocked' WHERE id = $1", [user_id])

async def unblock_user(user_id: int) -> bool:
    return await update_query("UPDATE users SET status = 'activated' WHERE id = $1", [user_id])

async def approve_user(email: EmailStr) -> bool:
    return await update_query("UPDATE users SET status = 'activated' WHERE email = $1", [email])

async def check_if_not_admin(current_user_id: int) -> bool:
    data = await read_query("SELECT COUNT(*) FROM users WHERE id = $1 AND is_admin = TRUE", [current_user_id])
    return data[0][0] == 0

async def view_user_transactions(user_id: int, current_user: int, filters: TransactionFilters):
    admin_status = await read_query('SELECT is_admin FROM users WHERE id = $1', [current_user])
    if not admin_status or not admin_status[0][0]:
        return "Not authorized. Must be an admin"

    query = """
        SELECT status, transaction_date, amount, sender_id, receiver_id, cards_id 
        FROM transactions 
        WHERE (sender_id = $1 OR receiver_id = $2)
    """
    params = [user_id, user_id]

    if filters.start_date:
        query += " AND transaction_date >= $3"
        params.append(filters.start_date)
    if filters.end_date:
        query += " AND transaction_date <= $4"
        params.append(filters.end_date)
    if filters.sender_id:
        query += " AND sender_id = $5"
        params.append(filters.sender_id)
    if filters.recipient_id:
        query += " AND receiver_id = $6"
        params.append(filters.recipient_id)
    if filters.direction:
        if filters.direction == 'incoming':
            query += " AND receiver_id = $7"
            params.append(user_id)
        elif filters.direction == 'outgoing':
            query += " AND sender_id = $8"
            params.append(user_id)

    query += f" ORDER BY {filters.sort_by} {filters.sort_order} LIMIT $9 OFFSET $10"
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

async def pending_transactions(current_user: int, user_id: int) -> str:
    admin_status = await read_query('SELECT is_admin FROM users WHERE id = $1', [current_user])
    if not admin_status or not admin_status[0][0]:
        return "Not authorized. Must be an admin"

    pending_transactions_data = await read_query("SELECT id, amount FROM transactions WHERE status = 'pending' AND sender_id = $1", [user_id])
    if not pending_transactions_data:
        return "There aren't any pending transactions."

    for transaction in pending_transactions_data:
        transaction_id = transaction[0]
        amount = transaction[1]
        await update_query("UPDATE transactions SET status = 'declined' WHERE id = $1", [transaction_id])
        await update_query("UPDATE users SET balance = balance + $1 WHERE id = $2", [amount, user_id])

    return "All pending transactions have been declined."
