import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router
from .settings import get_settings
from .hardware import initialize_hardware, cleanup_hardware

__version__ = '0.0.1'
exception_handlers = None

log = logging.getLogger(__name__)


def startup() -> None:
    '''Handle app startup'''

    settings = get_settings()
    # initialize_logging()
    # initialize_task_runner()
    # initialize_front_panel()
    initialize_hardware()
    # initialize_persistence()
    # initialize_notification()

    pass


def shutdown():
    '''Handle app shutdown'''

    # cleanup_notification()
    # cleanup_persistence()
    cleanup_hardware()
    # cleanup_front_panel()
    # cleanup_task_runner()

    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()
    yield
    shutdown()


app = FastAPI(
    title='OICP HTTP API Spec',
    description='This OpenAPI spec describes the HTTP API of the OICP Server.',
    version=__version__,
    lifespan=lifespan,
    exception_handlers=exception_handlers
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=('*'),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
    
app.include_router(router=router)
