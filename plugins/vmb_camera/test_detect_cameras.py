from time import sleep
from vmbpy import (  # type: ignore
    VmbSystem,
    Log,
    ScopedLogEnable,
    LOG_CONFIG_INFO_CONSOLE_ONLY
)


@ScopedLogEnable(LOG_CONFIG_INFO_CONSOLE_ONLY)
def print_device_id(dev , state ):
    msg = 'Device: {}, State: {}'.format(str(dev), str(state))
    Log.get_instance (). info(msg)


vmb: VmbSystem = VmbSystem.get_instance ()
vmb.register_camera_change_handler(print_device_id)
vmb.register_interface_change_handler(print_device_id)


with vmb:
    sleep(10)
