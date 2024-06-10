from data.models.categories import Category
from data.database_queries import read_query, insert_query, update_query


async def get_all(search=None, sort_by=None, page=1, size=10):
    sql = '''SELECT id, name FROM categories'''

    where_clauses = []
    params = []
    if search:
        where_clauses.append("name ILIKE $1")
        params.append(f"%{search}%")

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
    sql += f" LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([size, offset])

    results = await read_query(sql, params)
    return [Category.from_query_result(*row) for row in results]


async def create(category: Category):
    sql = 'INSERT INTO categories(name) VALUES($1) RETURNING id'
    params = (category.name,)

    result = await read_query(sql, params)
    category.id = result[0][0]
    return category


async def name_exists(name: str):
    sql = 'SELECT COUNT(*) FROM categories WHERE name = $1'
    params = (name,)

    data = await read_query(sql, params)
    return data[0][0] > 0


async def get_category_by_id(category_id: int) -> Category:
    '''
    This function retrieves a category from the database based on its ID.\n
    Parameters:\n
    - category_id : int\n
        - The ID of the category to retrieve.\n
    '''

    category_data = await read_query(sql='SELECT id, name FROM categories WHERE id = $1',
                                     sql_params=(category_id,))

    category = next((Category.from_query_result(*row) for row in category_data), None)

    return category
