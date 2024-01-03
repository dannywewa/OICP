import cv2
from vmbpy import *
import asyncio
import time

class VmbCameraBase:
    def __init__(self, *args):
        pass

    def init_camera(self):
        pass

    def flush(self):
        pass

    def queue_single_buffer(self, buf):
        pass

    def wait_buffer(self):
        pass

    def get_image_from_buffer(self, ny, nx, buffer):
        pass

    def get_serial_number(self):
        pass

    def set_integration_time(self, integration_time):
        pass

    def get_integration_time(self):
        pass

class VmbCamera(VmbCameraBase):
    def __init__(self, *args):
        super().__init__(self, *args)
        self.disarm_evt = asyncio.Event()

    def handler(self, cam, stream, frame):
        img = frame.as_numpy_ndarray()
        cv2.imwrite(f'capture_{self.id}.png', img)
        cam.queue_frame(frame)

    async def arm(self):

        with VmbSystem.get_instance() as vmb:
            cams = vmb.get_all_cameras()
            with cams[0] as cam:
                self.c = cam
                cam.set_pixel_format(PixelFormat.Mono8)
                cam.TriggerSource.set('Software')
                cam.TriggerSelector.set('FrameStart')
                cam.TriggerMode.set('On')
                cam.AcquisitionMode.set('Continuous')

                try:
                    s = cam.start_streaming(self.handler)
                    await self.disarm_evt.wait()
                finally:
                    cam.stop_streaming()

    async def disarm(self):
        self.disarm_evt.set()
        self.disarm_evt = asyncio.Event()

    async def capture(self, id):
        self.id = id
        self.c.TriggerSoftware.run()

class VmbCameraEmu(VmbCameraBase):
    pass
