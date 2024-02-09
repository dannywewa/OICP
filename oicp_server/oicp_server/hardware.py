from fastapi import FastAPI
from starlette.datastructures import State
from oicp_hardware.sensors.cameras.basler.camera import Basler

def initialize_hardware(state: State):
    '''Initialize the hardware API singleton, attaching it to global state.'''

    state.camera = Basler()
    state.camera.init_controller()

def cleanup_hardware(state: State):
    '''Shutdown the hardware API singleton and remove it from global state.'''
    state.camera.stop()