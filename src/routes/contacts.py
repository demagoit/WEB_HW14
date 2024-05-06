from fastapi import APIRouter, HTTPException, status, Path, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.database.schemas import RecordSchema, RecordUpdateSchema, RecordResponseSchema
from src.database.models import User
from src.repository import contacts as rep_contacts
from src.services.auth import auth_service
from src.conf.config import route_rst

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/healthchecker', dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def healthchecker(db: AsyncSession = Depends(get_db)):
    '''
    helth checker endpoint

    :db (AsyncSession): async db session Default=Depends(get_db)
    :return (dict | None): succes message or exception

    '''
    try:
        result = await db.execute(text('SELECT 1'))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail='Database is not configured corectly')
        return {'message': 'Welcome to Contacts app!'}
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=500, detail='Error connecting to database')


@router.get("/", response_model=list[RecordResponseSchema], dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def get_contacts(limit: int = Query(default=10, ge=1, le=50, description="Records per response to show"), 
                       offset: int = Query(
                           default=0, ge=0, description="Records to skip in response"),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    '''
    Retrieves a list of contacts for a specific user with specified pagination parameters.
    
    Args:
        current_user: The user to retrieve contacts for.
        limit: The maximum number of contacts to return.
        offset: The number of contacts to skip.
        db: async db session
    Returns:
        obj: 'list' of obj: User: A list of contacts.
    '''
    result = await rep_contacts.get_contacts(user=current_user, limit=limit, offset=offset, db=db)
    return result


@router.get("/query", response_model=list[RecordResponseSchema], dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def get_contacts_query(first_name: str | None = Query(default=None, description="Pattern to search in First name"),
                           last_name: str | None = Query(
                               default=None, description="Pattern to search in Last name"),
                           email: str | None = Query(
                               default=None, description="Pattern to search in e-mail"),
                           days_to_birthday: int | None = Query(default=None, le=30, description="Filter contacts with birthday in given days"),
                           limit: int = Query(default=10, ge=1, le=50, description="Records per response to show"), 
                           offset: int = Query(default=0, ge=0, description="Records to skip in response"),
                           db: AsyncSession = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    '''
    Retrieves a list of contacts with pecific search pattern for a specific user with specified pagination parameters.

    Args:        
        first_name: Pattern to search in First name, default=None
        last_name: Pattern to search in Last name, default=None
        email: Pattern to search in e-mail, default=None
        days_to_birthday: Filter contacts with birthday in given days, max=30 days, default=None
        limit: The maximum number of contacts to return. min=1, max=50, default=10
        offset: The number of contacts to skip. min=0, default=0
        current_user: The user to retrieve ontacts for.
        db: async db session Default=Depends(get_db)
    Returns:
        obj: 'list' of obj: 'Record': A list of contacts.
    '''
    result = await rep_contacts.get_contacts_query(user=current_user, first_name=first_name, last_name=last_name, email=email, days_to_birthday=days_to_birthday,
                                                   limit=limit, offset=offset, db=db)
    return result


@router.get("/{rec_id}", response_model=RecordResponseSchema, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def get_contact(rec_id: int = Path(description="ID of record to search"),
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    '''
    Retrieves contacts by ID for a specific user.
    
    Args:
        rec_id: ID of record to search
        current_user: The user to retrieve ontacts for.
        db: async db session Default=Depends(get_db)
    Returns:
        obj: 'Record' | None: Contact with given ID or None.
    '''
    result = await rep_contacts.get_contact(user=current_user, record_id=rec_id, db=db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Record ID not found')
    return result


@router.post("/", response_model=RecordResponseSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def create_contact(body: RecordSchema, db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    '''
    Creates new contact for a specific user.

    Args:    
        body: data of new contact record
        current_user: The user to retrieve ontacts for.
        db: async db session Default=Depends(get_db)
    Returns:
        obj: 'Record' | None: Contact with ID or None.
    '''
    result = await rep_contacts.create_contact(user=current_user, body=body, db=db)
    return result


@router.put("/{rec_id}", response_model=RecordResponseSchema, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def update_contact(body: RecordUpdateSchema, 
                         rec_id: int = Path(description="ID of record to change"), 
                         db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)):
    '''
    Updates contact for a specific user.

    Args:    
        body: updated data of the contact record
        rec_id: ID of record to change
        current_user: The user to retrieve ontacts for.
        db: async db session Default=Depends(get_db)
    Returns:
        obj: 'Record' | None: Contact with ID or None.
    '''
    result = await rep_contacts.update_contact(user=current_user, record_id=rec_id, body=body, db=db)
    return result


@router.delete("/{rec_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(route_rst.rate_limiter)], description=route_rst.restict_descr)
async def delete_contact(rec_id: int = Path(description="ID of record to delete"), db: AsyncSession = Depends(get_db), 
                         current_user: User = Depends(auth_service.get_current_user)):
    '''
    Deletes contact for a specific user.

    Args:    
        rec_id: ID of record to delete
        current_user: The user to retrieve ontacts for.
        db: async db session Default=Depends(get_db)
    Returns:
        None
    '''
    result = await rep_contacts.delete_contact(user=current_user, record_id=rec_id, db=db)
    return result
