from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query


def get_all(search=None, sort_by=None, page=1, size=10):
    sql = '''SELECT id, name FROM categories'''

    where_clauses = []
    if search:
        where_clauses.append(f"name like '%{search}%'")

    if where_clauses:
        sql += ' WHERE ' + ' AND '.join(where_clauses)

    if sort_by:
        valid_sort_fields = ['id', 'name']
        if sort_by.split(':')[0] in valid_sort_fields:
            sort_field, sort_order = sort_by.split(':')
            if sort_order.upper() == 'DESC':
                sql += f" ORDER BY {sort_field} DESC"
            else:
                sql += f" ORDER BY {sort_field}"
        else:
            raise ValueError("Invalid sort_by parameter")

    offset = (page - 1) * size
    sql += f" LIMIT {size} OFFSET {offset}"

    return (Category.from_query_result(*row) for row in read_query(sql))


def create(category: Category):
    generated_id = insert_query(
        'INSERT INTO categories(name) VALUES(?)',
        (category.name,))

    category.id = generated_id
    return category


def name_exists(name: str):
    data = read_query('SELECT COUNT(*) from categories WHERE name = ?', (name,))
    if data == [(0,)]:
        return False

    return True