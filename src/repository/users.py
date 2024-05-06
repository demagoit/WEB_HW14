from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User
from src.database.schemas import UserDBSchema


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    '''
    find user in db by given e-mail

    Args:
        email: user's e-mail
        db: async db session
    Returns:
        obj: 'User' | None: returns user record from db
    '''
    stmt = select(User).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(body: UserDBSchema, db: AsyncSession) -> User:
    '''
    create new user in db

    Args:
        body: new user data
        db: async db session
    Returns:
        obj: 'User': returns user record from db
    '''
    user = User(**body.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_token(user: User, token: str | None, db: AsyncSession) -> User:
    '''
    update refresh token of user in db

    Args:
        user: user to update
        token: new token or None
        db: async db session
    Returns:
        obj: 'User': returns user record from db
    '''
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)
    return user


async def user_email_confirmation(user: User, db: AsyncSession) -> User:
    '''
    set e-mail confirmation mark for user in db

    Args:
        user: user to update
        db: async db session
    Returns:
        obj: 'User': returns user record from db
    '''
    user.confirmed = True
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_avatar(user: User, url:str, db: AsyncSession) -> User:
    '''
    store url to user avatar in db

    Args:
        user: user to update
        url: url to stored avatar
        db: async db session
    Returns:
        obj 'User': returns user record from db
    '''
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
