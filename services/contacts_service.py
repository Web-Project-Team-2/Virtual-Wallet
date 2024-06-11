from data.models.contacts import Contact
from data.database_queries import read_query, insert_query
from common.responses import BadRequest


search_contacts = '''SELECT username, email, phone_number
                     FROM users 
                     WHERE username LIKE $1 OR email LIKE $1 OR phone_number LIKE $1'''

id_contacts = '''SELECT users_id, contact_user_id
                 FROM contacts
                 WHERE users_id = $1'''

values_contacts = '''INSERT INTO contacts(users_id, contact_user_id) 
                     VALUES($1, $2)'''


async def view_all_contacts(current_user: int,
                            search: str | None = None):
    '''
    This function returns a list of all the contacts a specified user has.\n
    Parameters:\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.\n
    - search: str | None\n
        - Searches for contacts by a specific username, email, or phone number.
    '''
    if search is None: 
        contacts = await read_query(sql=id_contacts,
                                    sql_params=(current_user,))
    else:
        search_by = f'%{search}%'
        contacts = await read_query(sql=search_contacts,
                                    sql_params=(search_by,))
        
        return contacts[0]

    contacts_all = []
    for row in contacts:
        contact = Contact.from_query_result(*row)
        if contact not in contacts_all:
            contacts_all.append(contact)

    if contacts_all:
        return contacts_all
    else:
        return None


async def view_contact_by_id(contact_user_id: int):
    '''
    This function returns a more detailed information about a user's transactions.\n
    Parameters:\n
    - contact_user_id: int\n
        - The ID of the contact for which detailed information is requested..
    '''

    contact_by_id = await read_query(sql=id_contacts,
                                     sql_params=(contact_user_id,))
     
    contact = next((Contact.from_query_result(*row) for row in contact_by_id), None)

    return contact


async def create_contact(contact_user_id: int,
                         current_user: int):
    '''
    This function adds a contact to user's contact list.\n
    Parameters:\n
    - contact_user_id: int\n
        - The ID of the user to be added as a contact.\n
    - current_user: int\n
        - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
        - This parameter is used to ensure that the request is made by an authenticated user.
    '''

    user = current_user
    new_contact = contact_user_id

    create_contact = await insert_query(sql=values_contacts,
                                        sql_params=(user,
                                                    new_contact))

    if create_contact is not None:
        return create_contact
    else:
        return None


async def contact_id_exists(current_user: int,
                            reciever_id: int) -> bool:
    '''
    This function checks if a contact exists between the current user and the receiver.\n
    Parameters:\n
    - current_user : int\n
        - The ID of the current authenticated user.\n
    - reciever_id : int\n
        - The ID of the receiver to check the contact against.
    '''

    return any(await read_query(sql='''SELECT users_id, contact_user_id
                                                FROM contacts 
                                                WHERE users_id = $1 AND contact_user_id = $2''',
                                         sql_params=(current_user, reciever_id,)))

