from fastapi import APIRouter, Depends
from typing import List
from common.authorization import get_current_user
from common.responses import BadRequest, NotFound
from data.models.contacts import Contact
from schemas.contacts import ContactsViewAll, ContactView
from services import contacts_service, user_services


contacts_router = APIRouter(prefix='/api/contacts')


@contacts_router.get(path='/', response_model=List[ContactsViewAll], status_code=201, tags=['Contacts'])  
async def get_users_contacts(search: str | None = None,
                             current_user: int = Depends(dependency=get_current_user)):
   '''
   This function returns a list of all the contacts for the specified user.\n
   Parameters:\n
   - search: str | None\n
      - An optional search term to filter contacts by username, email, or phone number. If not provided, all contacts are returned.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   ''' 

   users_contacts = await contacts_service.view_all_contacts(current_user=current_user,
                                                             search=search)
   
   if users_contacts != [] or users_contacts != None:

      if search != None:
         username_contact = users_contacts[0]
         contact = [ContactsViewAll.contacts_view(username=username_contact)]
         return contact

      contacts_view = []
      for users_contact in users_contacts:
         users_contact = await user_services.get_user_by_id(user_id=users_contact.contact_user_id)
            
         if not users_contact:
            return NotFound(content='This contact is not available.')
         
         contacts_view.append(ContactsViewAll.contacts_view(username=users_contact.username))
      
      return contacts_view
      
   else:
      return NotFound(content=f'There are no available contacts.')


@contacts_router.get(path='/id/{contact_user_id}', response_model=List[ContactView], status_code=201, tags=['Contacts']) 
async def get_users_contact_by_id(contact_user_id: int,
                                  current_user: int = Depends(dependency=get_current_user)):
   '''
   This function returns a more detailed information about a user's contact\n
   Parameters:\n
   - contact_user_id: int\n
      - The ID of the contact whose details are being requested.\n
   - current_user : int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''
   
   if await contacts_service.contact_id_exists(current_user=current_user,
                                               reciever_id=contact_user_id):
      contact_view = await contacts_service.view_contact_by_id(contact_user_id=contact_user_id)
      user_contact = await user_services.get_user_by_id(user_id=contact_user_id)
      
      if contact_view is None:
         return NotFound(content='Required data not found.')
      else:
         contact_view = [ContactView.contacts_view(username=user_contact.username,
                                                   email=user_contact.email,
                                                   phone_number=user_contact.phone_number)]
         return contact_view
   else:
            return NotFound(content=f'The contact you are looking for is not available.')
   

@contacts_router.post(path='/', status_code=201, tags=['Contacts']) 
async def create_contact(contact: Contact,
                         current_user: int = Depends(dependency=get_current_user)):
   '''
   This function adds a user to another user's contact list.\n
   Parameters:\n
   - contact: Contact\n
      - An instance of the Contact model containing the details of the contact to be added.\n
   - current_user: int\n
      - The ID of the currently authenticated user, automatically injected by Depends(get_current_user).\n
      - This parameter is used to ensure that the request is made by an authenticated user.
   '''

   new_contact = await user_services.user_id_exists(user_id=contact.contact_user_id)
   if new_contact:
      contact_user_id = contact.contact_user_id
      contact_create = await contacts_service.create_contact(contact_user_id=contact_user_id,
                                                             current_user=current_user)
      user_contact = await user_services.get_user_by_id(user_id=contact_user_id)
      
      if user_contact is None:
         return NotFound(content='Required data not found.')
      else:
         contact_view = [ContactView.contacts_view(username=user_contact.username,
                                                   email=user_contact.email,
                                                   phone_number=user_contact.phone_number)]
         return contact_view

   else:
      return NotFound(content=f'The contact you are looking for is not available.')