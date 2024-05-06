from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime

from src.database.models import Record, User
from src.database.schemas import RecordSchema, RecordUpdateSchema


async def get_contacts(user: User, limit: int, offset: int, db: AsyncSession):
    '''
    Retrieves a list of contacts for a specific user with specified pagination parameters.
    
    Args:
        user: The user to retrieve contacts for.
        limit: The maximum number of contacts to return.
        offset: The number of contacts to skip.
        db: async db session
    Returns:
        obj: 'list' of obj: User: A list of contacts.
    '''
    stmt = select(Record).filter_by(
        user_id=user.id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contacts_query(user: User, first_name: str | None, last_name: str | None, email: str | None, days_to_birthday: int | None,
                             limit: int, offset: int, db: AsyncSession):
    '''
    Retrieves a list of contacts with pecific search pattern for a specific user with specified pagination parameters.

    Args:        
        user: The user to retrieve ontacts for
        first_name: Pattern to search in First name
        last_name: Pattern to search in Last name
        email: Pattern to search in e-mail
        days_to_birthday: Filter contacts with birthday in given days
        limit: The maximum number of contacts to return.
        offset: The number of contacts to skip.
        db: async db session
    Returns:
        obj: 'list' of obj: 'Record': A list of contacts.
    '''
    filters = [f"user_id={user.id}"]

    if first_name:
        filters.append(f"first_name LIKE '%{first_name}%'")
    if last_name:
        filters.append(f"last_name LIKE '%{last_name}%'")
    if email:
        filters.append(f"email LIKE '%{email}%'")
    if days_to_birthday:
        filters.append(
            f"(birthday-DATE_TRUNC('year', birthday)+DATE_TRUNC('year', CURRENT_DATE)) <= CURRENT_DATE+{days_to_birthday}")

    sql_text = text(
        f'SELECT * FROM records WHERE {" AND ".join(filters)}  LIMIT {limit} OFFSET {offset};')

    stmt = select(Record).from_statement(sql_text)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact(user: User, record_id: int, db: AsyncSession):
    '''
    Retrieves contacts by ID for a specific user.
    
    Args:
        user: The user to retrieve ontacts for.
        record_id: ID of record to search
        db: async db session
    Returns:
        obj: 'Record' | None: Contact with given ID or None.
    '''
    stmt = select(Record).filter_by(id=record_id, user_id=user.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(user: User, body: RecordSchema, db: AsyncSession):
    '''
    Creates new contact for a specific user.

    Args:    
        user: The user to retrieve ontacts for.
        body: data of new contact record
        db: async db session
    Returns:
        obj: 'Record' | None: Contact with ID or None.
    '''

    rec = Record(**body.model_dump())
    rec.user_id = user.id
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


async def update_contact(user: User, record_id: int, body: RecordUpdateSchema, db: AsyncSession):
    '''
    Updates contact for a specific user.

    Args:    
        user: The user to retrieve ontacts for.
        record_id: ID of record to change
        body: updated data of the contact record
        db: async db session
    Returns:
        obj: 'Record' | None: Contact with ID or None.
    '''
    stmt = select(Record).filter_by(id=record_id, user_id=user.id)
    result = await db.execute(stmt)
    result = result.scalar_one_or_none()
    if result:
        result.first_name = body.first_name
        result.last_name = body.last_name
        result.email = body.email
        result.birthday = body.birthday
        result.notes = body.notes
        result.updated_at = datetime.now()
        await db.commit()
        await db.refresh(result)
    return result

async def delete_contact(user: User, record_id: int, db: AsyncSession):
    '''
    Deletes contact for a specific user.

    Args:    
        user: The user to retrieve ontacts for.
        record_id: ID of record to delete
        db: async db session
    Returns:
        None
    '''
    stmt = select(Record).filter_by(id=record_id, user_id=user.id)
    result = await db.execute(stmt)
    result = result.scalar_one_or_none()
    if result:
        await db.delete(result)
        await db.commit()
    return result
