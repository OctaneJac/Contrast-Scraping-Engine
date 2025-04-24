from fastapi import FastAPI
from app.tasks import add

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI + Celery is running"}

@app.get("/add")
async def run_task(x: int = 1, y: int = 2):
    result = add.delay(x, y)
    return {"task_id": result.id}
