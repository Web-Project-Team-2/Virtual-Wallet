from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query

async def get_all(search=None, sort_by=None, page=1, size=10):
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

    results = await read_query(sql)
    return [Category.from_query_result(*row) for row in results]

async def create(category: Category):
    generated_id = await insert_query(
        'INSERT INTO categories(name) VALUES(%s)',
        (category.name,)
    )

    category.id = generated_id
    return category

async def name_exists(name: str):
    data = await read_query('SELECT COUNT(*) from categories WHERE name = %s', (name,))
    return data[0][0] > 0
