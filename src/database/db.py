import redis.asyncio as redis
import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from src.conf.config import config


class DatabaseSessionManager():
    '''
    initialize parameters of connection to database
    '''
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url=url)
        self._sessionmaker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        '''
        Creates async session instance

        Yelds:
            session: session instance
        Raises:
            Exception: If session parameters are not initialized or connection to database fails.
        '''
        if self._sessionmaker is None:
            raise Exception('db.py - Session is not initialized')
        session = self._sessionmaker()
        try:
            yield session
        except Exception as err:
            await session.rollback()
            print('Error in db.py')
            raise
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    '''
    manage session coonection to database

    Yelds:
        session: session instance
    '''
    async with sessionmanager.session() as session:
        yield session

rds_cache = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0,
                  encoding='utf-8', decode_responses=True)  # password=config.REDIS_PASSWORD,
