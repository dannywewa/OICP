from fastapi import APIRouter, Depends, status

from typing import Dict

router = APIRouter()

@router.get('/')
def get_root() -> Dict:
    return {'hello': 'world'}
