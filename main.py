import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from webthing import (
    Value,
    Thing,
    Subscriber,
    PropertyError,
    Action,
    Event,
    Property,
    SingleThing,
    MultipleThings,
)

import logging
import time
import uuid
import asyncio

from plugins.vmb_camera.api import VmbCamera

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8080/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

class OverheatedEvent(Event):

    def __init__(self, thing, data):
        Event.__init__(self, thing, 'overheated', data=data)


class FadeAction(Action):

    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'fade', input_=input_)

    def perform_action(self):
        time.sleep(self.input['duration'] / 500)
        self.thing.set_property('brightness', self.input['brightness'])
        self.thing.add_event(OverheatedEvent(self.thing, 102))
        if ws is not None:
            asyncio.run(ws.send_text("overheated"))

        print('action done internally')

class CaptureAction(Action):
    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'capture', input_=input_)

    async def perform_action(self):
        print(f'action: id={self.id}, name={self.name}')
        await self.thing.camera.capture(self.id)

class ArmAction(Action):
    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'arm', input_=input_)

    async def perform_action(self):
        print(f'action: id={self.id}, name={self.name}')
        await self.thing.camera.arm()

class DisarmAction(Action):
    def __init__(self, thing, input_):
        Action.__init__(self, uuid.uuid4().hex, thing, 'disarm', input_=input_)

    async def perform_action(self):
        print(f'action: id={self.id}, name={self.name}')
        await self.thing.camera.disarm()

class MyThing(Thing):
    def __init__(self):
        super().__init__(
            'urn:dev:ops:my-lamp-1234',
            'My Lamp',
            ['OnOffSwitch', 'Light'],
            'A web connected lamp',
        )

        self.camera = VmbCamera()

        self.add_property(
            Property(self,
                    'on',
                    Value(True),
                    metadata={
                        '@type': 'OnOffProperty',
                        'title': 'On/Off',
                        'type': 'boolean',
                        'description': 'Whether the lamp is turned on',
                    }))
        self.add_property(
            Property(self,
                    'brightness',
                    Value(50),
                    metadata={
                        '@type': 'BrightnessProperty',
                        'title': 'Brightness',
                        'type': 'integer',
                        'description': 'The level of light from 0-100',
                        'minimum': 0,
                        'maximum': 100,
                        'unit': 'percent',
                    }))

        self.add_available_action(
            'fade',
            {
                'title': 'Fade',
                'description': 'Fade the lamp to a given level',
                'input': {
                    'type': 'object',
                    'required': [
                        'brightness',
                        'duration',
                    ],
                    'properties': {
                        'brightness': {
                            'type': 'integer',
                            'minimum': 0,
                            'maximum': 100,
                            'unit': 'percent',
                        },
                        'duration': {
                            'type': 'integer',
                            'minimum': 1,
                            'unit': 'milliseconds',
                        },
                    },
                },
            },
            FadeAction)

        self.add_available_action(
            'arm',
            {
                'title': 'Arm',
            },
            ArmAction,
        )

        self.add_available_action(
            'disarm',
            {
                'title': 'Disarm',
            },
            DisarmAction,
        )

        self.add_available_action(
            'capture',
            {
                'title': 'Capture',
                'input': {
                    'type': 'object',
                    'required': [
                        'integration time'
                    ],
                    'properties': {
                        'integration time': {
                            'type': 'integer',
                            'minimum': 0,
                            'maximum': 1000000,
                            'unit': 'us',
                        }
                    }
                }
            },
            CaptureAction,
        )

        self.add_available_event(
            'overheated',
            {
                'description':
                'The lamp has exceeded its safe operating temperature',
                'type': 'number',
                'unit': 'degree celsius',
            })


thing = MyThing()

ws = None

@app.get('/')
async def root():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global ws
    await websocket.accept()
    ws = websocket

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.get('/properties')
async def get_properties():
    return thing.get_properties()

@app.put('/properties/{property_name}')
async def put_property_by_name(property_name: str, p: int):
    print(property_name)
    print(p)
    thing.set_property(property_name, p)

@app.get('/properties/{property_name}')
async def get_property_by_name(property_name: str):
    print(property_name)
    p = thing.get_property(property_name)
    return { property_name: p}

@app.get('/actions')
async def get_actions():
    return thing.get_action_descriptions()

@app.get('/actions/{action_name}/{action_id}')
async def get_action_by_name_id(action_name: str, action_id: str):
    action = thing.get_action(action_name, action_id)
    return action.as_action_description()

@app.post('/actions/{action_name}')
async def post_actions(action_name: str):
    if action_name == 'capture':
        input = {'integration time': 1000}
        action = thing.perform_action('capture', input)
        response = action.as_action_description()
    elif action_name == 'arm':
        action = thing.perform_action('arm')
        response = action.as_action_description()
    elif action_name == 'disarm':
        action = thing.perform_action('disarm')
        response = action.as_action_description()

    # asyncio.get_event_loop().run_in_executor(None, action.start)
    asyncio.create_task(action.start())

    return response


@app.get('/events/{event_name}')
async def get_event_by_name(event_name: str):
    return thing.get_event_descriptions(event_name)

@app.get('/events')
async def get_events():
    return thing.get_event_descriptions()

    
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
