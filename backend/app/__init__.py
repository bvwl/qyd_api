from fastapi import APIRouter
from app.apis import apis_router

app = APIRouter()
app.include_router(apis_router)
