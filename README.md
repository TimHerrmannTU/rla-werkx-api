### Run as Development
python -m uvicorn main:app --reload

### Run as Production
docker compose up --build

### Run Alembic Migration
```
python -m alembic stamp head
python -m alembic revision --autogenerate -m "name of the change"
python -m alembic upgrade head
```