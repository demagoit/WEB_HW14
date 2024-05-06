from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
import pickle
from src.database.db import get_db, rds_cache
from src.repository import users as rep_users
from src.conf.config import config

class Auth():
    '''
    Class to proccess user authentification
    '''

    pwd_context = CryptContext(schemes=['bcrypt'])
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    SECRET_KEY = config.SECRET_JWT
    ALGORITHM = config.ALGORITHM_JWT
    cache = rds_cache

    def verify_password(self, plaine_pwd: str, hashed_pwd: str) -> bool:
        '''
        verify password

        Args:
            plaine_pwd: readable password 'as is'
            hashed_pwd: hashed password to compare with
        Returns:
            bool: True if success False othervise
        '''

        return self.pwd_context.verify(plaine_pwd, hashed_pwd)

    def get_pasword_hash(self, password: str) -> str:
        '''
        make hash of the plain password

        Args:
            password: readable password 'as is'
        Returns:
            'str': hashed password
        '''
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[int] = 15) -> str:
        '''
        creates access token

        Args:
            data: data to include in the tocken
            expires_delta: token expiration time. Optional. Default - 15 min
        Returns:
            'str': encoded access token
        '''
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expires_delta)
        to_encode.update(
            {'iat': now.timestamp(), 'exp': expire.timestamp(), 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, key=self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[int] = 7*24*60) -> str:
        '''
        creates refresh token

        Args:
            data: data to include in the tocken
            expires_delta: token expiration time. Optional. Default - 7 days
        Returns:
            'str': encoded refresh token
        '''
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expires_delta)
        to_encode.update(
            {'iat': now.timestamp(), 'exp': expire.timestamp(), 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(
            to_encode, key=self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def create_email_token(self, data: dict, expires_delta: Optional[int] = 7*24*60) -> str:
        '''
        creates e-mail confirmation token

        Args:
            data: data to include in the tocken
            expires_delta: token expiration time. Optional. Default - 7 days
        Returns:
            'str': encoded e-mail token
        '''
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expires_delta)
        to_encode.update(
            {'iat': now.timestamp(), 'exp': expire.timestamp(), 'scope': 'email_token'})
        encoded_email_token = jwt.encode(
            to_encode, key=self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_email_token

    async def decode_token(self, token: str, scope: str) -> str:
        '''
        decode and verify token

        Args:
            token: token to decode and verify
            scope: scope of the token to be checked 
        Returns:
            'str' | None: e-mail from the token
        Raises:
            HTTPException: If wrong scope of the token or invalid token
        '''
        try:
            payload = jwt.decode(token=token, key=self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == scope:
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope of token')
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token=Depends(oauth2_scheme), db: AsyncSession=Depends(get_db)):
        '''
        get user by access token

        Args:
            token: access token. Default = Depends(oauth2_scheme)
            db: async db session. Default = Depends(get_db)
        Returns:
            obj: 'User' | None: user db record
        Raises:
            HTTPException: If Invalid scope of the token or invalid token
        '''
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token=token, key=self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credential_exception
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope of token')
        except JWTError:
            raise credential_exception
        
        user = await self.cache.get(f'user:{email}')
        if user is None:
            user = await rep_users.get_user_by_email(email=email, db=db)
            if user is None:
                raise credential_exception
            await self.cache.set(f'user:{email}', pickle.dumps(user))
            await self.cache.expire(f'user:{email}', 900)
        else:
            user = pickle.loads(user)
        return user

auth_service = Auth()