from fastapi import FastAPI, APIRouter, Depends, status, Request, Response
import asyncio
from typing import Dict, List

from oicp_hardware.sensors.cameras.basler.camera import Basler

router = APIRouter()


@router.get("/")
def get_root() -> Dict:
    return {"hello": "world"}
