import uvicorn
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get('/')
async def read_root():
    return {'Hello': 'World'}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: str | None = None):
    return {'item_id': item_id, 'q': q}
