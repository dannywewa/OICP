import cv2
from vmbpy import (  # type: ignore
    VmbSystem,
    Camera,
    Frame,
    Stream,
    FrameStatus,
    PixelFormat,
    CameraEvent,
)
import asyncio
from enum import StrEnum, auto
from pyee import EventEmitter
import numpy as np


class PxielFormat(StrEnum):
    Mono8 = auto()
    Mono10 = auto()
    Mono12 = auto()


class BinningMode(StrEnum):
    Sum = auto()
    Average = auto()


class TriggerSource(StrEnum):
    FreeRun = auto()
    Software = auto()
    FixedRate = auto()
    Line1 = auto()
    Line2 = auto()
    Line3 = auto()
    Line4 = auto()


class TriggerActivation(StrEnum):
    RisingEdge = auto()
    FallingEdge = auto()
    AnyEdge = auto()
    LevelHigh = auto()
    LevelLow = auto()


class CameraStatus(StrEnum):
    Connected = auto()
    Disconnected = auto()
    Streaming = auto()
    Capturing = auto()
    Acquiring = auto()


class CameraEventType(StrEnum):
    FrameReady = auto()
    StatusChanged = auto()


class CameraBase(EventEmitter):
    def __init__(self):
        pass

    async def get_exposure_time(self):
        pass

    async def set_exposure_time(self, value):
        pass

    async def get_height(self):
        pass

    async def get_width(self):
        pass

    async def get_gain(self):
        pass

    async def set_gain(self, value):
        pass

    async def get_trigger_source(self):
        pass

    async def set_trigger_source(self, value):
        pass

    async def get_trigger_activation(self):
        pass

    async def set_trigger_activation(self, value):
        pass

    async def get_horizontal_binning_mode(self):
        pass

    async def set_horizontal_binning_mode(self, value):
        pass

    async def get_vertical_binning_mode(self):
        pass

    async def set_vertical_binning_mode(self):
        pass

    def is_grabbing(self):
        pass

    def is_streaming(self):
        pass

    def is_capturing(self):
        pass

    def is_acquiring(self):
        pass

    def status(self):
        pass

    def grab_one(self, timeout):
        pass

    def grab_many(self, count, timeout):
        pass

    def notify(self, event, data):
        pass


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


class VmbCamera(VmbCameraBase, EventEmitter):
    def __init__(self, *args):
        VmbCameraBase.__init__(self, *args)
        EventEmitter.__init__(self, *args)

        self.disarm_evt = asyncio.Event()
        self.opened_evt = asyncio.Event()
        self.closed_evt = asyncio.Event()
        print(self.closed_evt)
        self.image_ready_evt = asyncio.Event()
        self.shutdown_evt = asyncio.Event()

        self.is_initialized = False
        self.is_opened = False
        self.is_armed = False

        self.vmb: VmbSystem = VmbSystem.get_instance()
        self.vmb.register_camera_change_handler(self.camera_changed)
        self.vmb.register_interface_change_handler(self.interface_changed)

        self.cam: Camera

        self.on("camera changed", self.on_camera_changed)

    def camera_changed(self, dev, state):
        print("camera changed: {}, {}".format(dev, state))
        if state == CameraEvent.Missing:
            asyncio.run(self.close())
        elif state == CameraEvent.Detected:
            # asyncio.run(self.open())
            # asyncio.create_task(self.open_task())
            self.emit("camera changed", "Detected")

    def interface_changed(self, dev, state):
        print("interface changed: {}, {}".format(dev, state))

    def on_camera_changed(self, d):
        asyncio.run(self.open())

    def handler(self, cam: Camera, stream: Stream, frame: Frame):
        if frame.get_status() == FrameStatus.Complete:
            img = frame.as_numpy_ndarray()
            print("mean: {}".format(np.mean(img)))
            print("histo: {}".format(np.histogram(img, bins=10, range=(0, 1023))))
            cv2.imwrite(f"capture_{self.id}.png", img)
            self.image_ready_evt.set()
        cam.queue_frame(frame)

    async def init_task(self):
        self.vmb = VmbSystem.get_instance()
        if not self.is_initialized:
            with self.vmb:
                self.is_initialized = True
                print("initialized camera system")
                await self.shutdown_evt.wait()
                self.shutdown_evt = asyncio.Event()
                print("deinitialized camera system")
            self.is_armed = False
            self.is_opened = False
            self.is_initialized = False

    async def deinit_task(self):
        self.shutdown_evt.set()

    async def open_task(self):
        if not self.is_opened:
            with self.vmb:
                cams = self.vmb.get_all_cameras()
                self.cam = cams[0]
                # self.opened_evt.set()
                print("opened")
                self.is_opened = True
                print("waiting for closed_evt to be set: {}".format(self.closed_evt))

                await self.closed_evt.wait()
                print("closed")
                self.closed_evt = asyncio.Event()
                print(self.closed_evt)
                self.is_armed = False
                self.is_opened = False

    async def init(self):
        print("initializing camera system")
        asyncio.create_task(self.init_task())

    async def deinit(self):
        print("deinitializing camera system")
        asyncio.create_task(self.deinit_task())

    async def open(self):
        print("opening")
        asyncio.create_task(self.open_task())

    async def close(self):
        print("setting the closed_evt: {}".format(self.closed_evt))
        self.closed_evt.set()
        print("closing")

    async def arm_task(self, input=None):
        if not self.is_armed:
            with self.cam as cam:
                print("arming software triggering")
                cam.set_pixel_format(PixelFormat.Mono8)
                if input:
                    cam.ExposureTime.set(input["exposure_time_hint"])
                cam.TriggerSource.set("Software")
                cam.TriggerSelector.set("FrameStart")
                cam.TriggerMode.set("On")
                cam.AcquisitionMode.set("Continuous")

                try:
                    cam.start_streaming(self.handler)
                    print("armed software triggering")
                    self.is_armed = True
                    await self.disarm_evt.wait()
                finally:
                    cam.stop_streaming()
                    print("disarmed software triggering")
                    self.disarm_evt = asyncio.Event()
                    self.is_armed = False

    async def arm_swtrigger(self, input=None):
        asyncio.create_task(self.arm_task(input))

    async def disarm_swtrigger(self):
        self.disarm_evt.set()
        print("disarming software triggering")

    async def capture0(self, id):
        self.id = id
        with self.cam as c:
            f = c.get_frame()
            print(f)

    async def capture(self, id):
        self.id = id
        with self.cam as c:
            c.TriggerSoftware.run()

    async def capture_swtrigger(self, id, integration_time):
        """
        Software triggering
        """
        self.id = id
        with self.cam as cam:
            try:
                await self.set_integration_time(integration_time)
                cam.TriggerSoftware.run()
            except Exception:
                pass

    async def set_integration_time(self, integration_time: int):
        self.cam.ExposureTime.set(integration_time)
