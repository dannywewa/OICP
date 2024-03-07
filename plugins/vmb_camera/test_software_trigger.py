# Software trigger for continuous image acquisition

import time
from vmbpy import (  # type: ignore
    VmbSystem,
)


def handler(cam, stream, frame):
    print("Frame acquired: {}".format(frame), flush=True)
    cam.queue_frame(frame)


def main():
    with VmbSystem.get_instance() as vmb:
        cam = vmb.get_all_cameras()
        with cam[0] as camera:
            camera.TriggerSource.set("Software")
            camera.TriggerSelector.set("FrameStart")
            camera.TriggerMode.set("On")
            camera.AcquisitionMode.set("Continuous")

            try:
                camera.start_streaming(handler)

                for i in range(200):
                    time.sleep(0.03)
                    camera.TriggerSoftware.run()
            except Exception as e:
                print(e)
            finally:
                camera.stop_streaming()


if __name__ == "__main__":
    main()
