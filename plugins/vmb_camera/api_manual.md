# Python API Manual
[api doc](https://docs.alliedvision.com/Vimba_X/Vimba_X_DeveloperGuide/pythonAPIManual.html)

## Intro

The Python API (VmbPy) is a Python wrapper around the VmbC API. It provides
all functions from VmbC, but enables you to program with less lines of code.

We recommend using VmbPy for:

- Quick prototyping
- Getting started with programming machine vision or embedded vision
applications
- Easy interfacing with deep learning frameworks and libraries such as
OpenCV via NumPy arrays

## General aspects of the API

The entry point of VmbPy is the Vimba X singleton representing the underlying
Vimba X System.

The Vimba X singleton implements a context manager. The context entry
initializes:

- System features discovery
- Interface and transport layer (TL) detection
- Camera detection

The context entry always handles:

- API startup (including an optional method for advanced TL configuration) and
shutdown
- Opening and closing cameras, interfaces, and TLs
- Feature discovery for the opened entity

Always call all methods for Camera, Feature, and Interface within the scope of
a `with` statement:

```Python
from vmbpy import *

with VmbSystem.get_instance() as vmb:
    cams = vmb.get_all_cameras()
```

**`class Camera`**

The Camera class implements a context manager. On entering the Camera's
context, all camera features are detected and can be accesse only with the
`with` statement.

**`class Frame`**

The Frame class stores raw image data and metadata of a single frame. The
frame class implements deepcopy semantics.

The following code snippet shows how to:

- Acquire a single frame
- Convert the pixel format to Mono8
- Store it using opencv-python

```Python
import cv2
from vmbpy import VmbSystem

with VmbSystem.get_instance() as vmb:
    cams = vmb.get_all_cameras()
    with cams[0] as cam:
        frame = cam.get_frame()
        frame.convert_pixel_format(PixelFormat.Mono8)
        cv2.imwrite('frame.jpg', frame.as_opencv_image())
```

**`class Interface`**

The Interface class contains all data of detected hardware interfaces cameras
are connected to.

```Python
from vmbpy import *

with VmbSystem.get_instance () as vmb:
    inters = vmb.get_all_interfaces ()
    with inters [0] as interface:
        for feat in interface.get_all_features ():
            print(feat)
```

## Image Capture vs Image Acquisition

Image capture and image acquisition are two independent operations: The API
captures images, the camera acquires images. To obtain an image from your
camera, setup the API to capture images before starting the acquisition on
the camera:

Typical asynchronous application using VmbC:

1. **Prepare image acquisition**:
    - Make API aware of buffers: `VmbFrameAnnounce()`
    - Start the capture engine: `VmbCaptureStart()`
    - Hand buffers over to API: `VmbCaptureFrameQueue()`
2. **Start image acquisition**
    - Run camera command feature: `AcquisitionStart()`
3. **Image is within callback function**
    - Requeue frame: `VmbCaptureFrameQueue()`
4. **Stop image acquisition**
    - Run camera command: `AcquisitionStop()`
5. **Clean up**
    - Discard pending frame callbacks and stop capture engine: `VmbCaptureEnd()`
    - Flush the capture queue: `VmbCaptureQueueFlush()`
    - Revoke all frames: `VmbFrameRevokeAll()`

### Image capture

To enable image capture, frame buffers must be allocated and the API must be
prepared for incoming frames.

To capture images sent by the camera, follow these steps:

1. Open the camera
2. Query the necessary buffer size through the convenience function
`VmbPayloadSizeGet()`
3. Announce the frame buffers. If you announce NULL buffers, the TL announces
buffers with a suitable value.
4. Start the capture engine.
5. Queue the frame you have just created with `VmbCaptureFrameQueue()`, so
that the buffer can be filled when the acquisition has started.

The API is now ready. Start and stop image acquisition on the camera. How you
proceed depens on the acquisition model you need:

- Synchronous: Use VmbCaptureFrameWait to receive an image frame while
blocking your execution thread.
- Asynchronous: Register a callback that gets executed when capturing is
complete. 
6. Stop the capture engine and discard all pending callbacks with
`VmbCaptureEnd()`
7. Call `VmbCaptureQueueFlush()` to cancel all frames on the queue.
8. Revoke the frames with `VmbFrameRevokeAll()` to clear the buffers.

### Image Acquisition

As soon as the API is prepared, you can start acquisition on your camera:

1. Set the feature *AcquisitionMode* (for example: Continuous).
2. Run the command **AcquisitionStart**
3. To stop image acquisition, run command **AcquisitionStop**.

## API Usage

### Listing cameras

Camera and hardware interfaces such as USB can be detected at runtime by
registering a callback at the Vimba X instance.

```Python
from time import sleep
from vmbpy import *

@ScopedLogEnable(LOG_CONFIG_INFO_CONSOLE_ONLY)
def print_device_id(dev , state ):
    msg = 'Device: {}, State: {}'.format(str(dev), str(state ))
    Log.get_instance (). info(msg)

vmb VmbSystem = VmbSystem.get_instance ()
vmb.register_camera_change_handler(print_device_id)
vmb.register_interface_change_handler(print_device_id)

with vmb:
    sleep (10)
```

### Listing features

### Accessing features

The following code snippet shows how to read and write exposure time.

```Python
from vmbpy import *

with VmbSystem.get_instance () as vmb:
    cams = vmb.get_all_cameras ()
    with cams [0] as cam:
        exposure_time = cam.ExposureTime

        time = exposure_time.get()
        inc = exposure_time.get_increment ()

        exposure_time.set(time + inc)
```

### Acquiring images

The Camera class supports synchronous and asynchronous image acquisition. For
high performance, acquire frames asynchronously and keep the registered
callable as short as possible.

To activate "alloc and announce" (optional): Use optional parameter /x to
overwrite `allocation_mode`.

```Python
# Synchronous grab
from vmbpy import *

with VmbSystem.get_instance () as vmb:
    cams = vmb.get_all_cameras ()
    with cams [0] as cam:
        # Aquire single frame synchronously
        frame = cam.get_frame ()

        # Aquire 10 frames synchronously
        for frame in cam.get_frame_generator(limit =10):
            pass
```

Acquire frames asynchronously by registering a callable being executed with
each incoming frame:

```Python
# Asynchronous grab
import time
from vmbpy import*

def frame_handler(cam , frame ):
    cam.queue_frame(frame)

with VmbSystem.get_instance () as vmb:
    cams = vmb.get_all_cameras ()
    with cams [0] as cam:
        cam.start_streaming(frame_handler)
        time.sleep (5)
        cam.stop_streaming ()
```

### Changing the pixel format

Always use the convenience functions instead of the PixelFormat feature of
the Camera. The convenience function `set_pixel_format(fmt)` changes the
Camera pixel format by passing the desired member of the `PixelFormat` enum.

```Python
# Camera class methods for getting and setting pixel formats
# Apply these methods before starting image acquisition

get_pixel_formats () # returns a tuple of all pixel formats supported by the camera
get_pixel_format () # returns the current pixel format
set_pixel_format(fmt) # enables you to set a new pixel format
```

**Note:** The pixel format cannot be changed while the camera is acquiring
images.

After image acquisition in the camera, the Frame contains the pixel format of
the camera. Now you can convert the pixel format with the
`convert_pixel_format()` method.

### Listing chunk data

Chunk data are image metadata such as the exposure time that are avaiable in
the Frame. To activate chunk, see the user documentation of your camera.

```Python
# Before using chunk, open your camera as usual
def chunk_callback(features: FeatureContainer):
    print(f'Chunk callback executed for frame with id {features.ChunkFrameID.get()}')

def frame_callback(cam: Camera, stream: Stream, frame: Frame):
    print(f'Frame callback executed for {frame}')

    # Calling this method only works if chunk mode is activated!
    frame.access_chunk_data(chunk_callback)
    stream.queue_frame(frame)

try:
    cam.start_streaming(frame_callback),
    time.sleep(1)
finally:
    cam.stop_streaming()
```

### Loading and saving user sets

see 'test_user_set.py'

### Loading and saving settings

Additionally to the user sets stored in the camera, you can save the feature
values as an XML file to your host PC.

see 'test_load_save_settings.py'

### Software trigger

Software trigger commands are supported. To get started with triggering and
explore the possibilities, you can use Vimba X Viewer.

To program a software trigger application, use the following code snippet:

```Python
# Software trigger for continuous image acquisition

import time
from vmbpy import VmbSystem

def handler(cam, stream, frame):
    print('Frame acquired: {}'.format(frame), flush=True)
    cam.queue_frame(frame)

def main():
    with VmbSystem.get_instance() as vmb:
        cam = vmb.get_all_cameras()
        with cam[0] as camera:
            camera.TriggerSource.set('Software')
            camera.TriggerSelector.set('FrameStart')
            camera.TriggerMode.set('On')
            camera.AcquisitionMode.set('Continuous')

            try:
                camera.start_streaming(handler)

                for i in range(200):
                    time.sleep(0.03)
                    camera.TriggerSoftware.run()
            except Exception:
                print(e)
            finally:
                camera.stop_streaming()

if __name__ == '__main__':
    main()
```

### Trigger over Ethernet - Action Commands

You can broadcast a trigger signal simultaneously to multiple GigE camera via
GigE cable. Action Commands must be set first to the camera(s) and then to the
API, which sends the Action Commands to the camera(s).

### Multithreading

The FrameConsumer thread displays images of the first detected camera via
OpenCV in a window of 480x480 pixels. The example automatically constructs,
starts, and stops FrameProducer threads for each connected or disconnected
camera.

### Logging

You can enable and configure logging to:

- Create error reports
- Prepare the migration to C API or the C++ API

```Python
from vmbpy import *

vmb VmbSystem = VmbSystem.get_instance()
vmb.enable_log(LOG_CONFIG_WARNING_CONSOLE_ONLY)

log = Log.get_instance ()
log.critical('Critical , visible ')
log.error('Error , visible ')
log.warning('Warning , visible ')
log.info('Info , invisible ')
log.trace('Trace , invisible ')

vmb.disable_log ()
```

The `ScopedLogEnable()` decorator allows enabling and disabling logging
on function entry and exit.

```Python
from vmbpy import *

@TraceEnable ()
def traced_function ():
   Log.get_instance (). info('Within Traced Function ')

@ScopedLogEnable(LOG_CONFIG_TRACE_CONSOLE_ONLY)
def logged_function ():
   traced_function ()

logged_function ()
```