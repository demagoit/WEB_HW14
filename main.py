from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import contextmanager

from src.routes import contacts, users
from src.conf.config import route_rst
from src.database.db import rds_cache


# replace depricated @app.on_event('startup')
@contextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(rds_cache)
    yield
app = FastAPI(lifespan=lifespan)

app = FastAPI()
app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins, 
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
    )

# @app.on_event('startup')
# async def startup():
#     await FastAPILimiter.init(rds_cache)

@app.get('/', dependencies=[Depends(route_rst.rate_limiter)])
def index():
    return {'message': 'Contacts application'}

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)