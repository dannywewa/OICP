from fastapi import FastAPI, APIRouter, Depends, status, Request, Response
import asyncio
from typing import Dict, List

from oicp_hardware.sensors.cameras.basler.camera import Basler

router = APIRouter()

@router.get('/')
def get_root() -> Dict:
    return {'hello': 'world'}

@router.get('/cameras')
def get_cameras() -> List:
    b = Basler()
    b.init_controller()
    b.init_dector()
    b.stop()
    return [str(b)]

    
@router.post('/open')
async def open(request: Request):
    ''''''
    camera: Basler = request.app.state.camera
    camera.init_dector()

@router.post('/close')
async def close(request: Request):
    camera: Basler = request.app.state.camera
    camera.stop()

@router.post('/grabone')
async def grab_one(request: Request):
    camera: Basler = request.app.state.camera
    img = camera.grab_data(1)
    return img.shape

@router.post('/shutdown')
async def shutdown():
    import os
    import signal
    os.kill(os.getpid(), signal.SIGTERM)
    return Response(status_code=200, content='gracefully shutting down ...')