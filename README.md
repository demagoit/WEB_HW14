FastAPI, Postgres, Redis, SQLAlchemy, Pydantic 

rename .env_example to .env and set configuration variables

mkdir bd_data

sudo docker compose up

chmod 777 -R bd_data/pgdata

python3 main.py

http://127.0.0.1:8000/docs#/

To geterate documentation with sphinx:
docs/make html