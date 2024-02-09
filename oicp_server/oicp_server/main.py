import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

import signal
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .router import router
from .settings import get_settings
from .service import initialize_logging
from .hardware import initialize_hardware, cleanup_hardware

__version__ = '0.0.1'
exception_handlers = None

log = logging.getLogger(__name__)


def startup(app: FastAPI) -> None:
    '''Handle app startup'''

    print('startup')
    settings = get_settings()
    initialize_logging()
    # initialize_task_runner()
    # initialize_front_panel()
    initialize_hardware(app.state)
    # initialize_persistence()
    # initialize_notification()

    pass


def shutdown(app: FastAPI):
    '''Handle app shutdown'''

    print('shutdown')
    # cleanup_notification()
    # cleanup_persistence()
    cleanup_hardware(app.state)
    # cleanup_front_panel()
    # cleanup_task_runner()

    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup(app)
    yield
    shutdown(app)


app = FastAPI(
    title='OICP HTTP API Spec',
    description='This OpenAPI spec describes the HTTP API of the OICP Server.',
    version=__version__,
    lifespan=lifespan,
    exception_handlers=exception_handlers
)


# Define the signal handler function
def graceful_shutdown(signum, frame):
    # Perform cleanup tasks here (e.g., closing database connections, saving state, etc.)
    # ...

    # Exit the application
    sys.exit(0)

# Register the signal handler for SIGTERM
signal.signal(signal.SIGTERM, graceful_shutdown)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=('*'),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
    
app.include_router(router=router)
