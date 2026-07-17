"""OSW12 Optical Switch interface.

On Linux to use the driver run the following command as root:
echo 1313 80e0 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id
"""

import time

from inspy.instrument._base import InstrumentBase, SerialInstrumentMixin
from inspy.utils import validate_args


class OpticalSwitchThorlabsOSW12(SerialInstrumentMixin, InstrumentBase):
    """Thorlabs OSW12 Optical Switch interface.

    For 2 State Switch (Thorlabs OSW12)
    State 1: In 2 -> Out 4 (Bare State)
    State 2: In 2 -> Out 3 (Cross State)


    `OSW12-1310E User Manual <https://www.thorlabs.com/drawings/16a5314a00f30022-7488CC39-F7CC-29A8-7315E81573D582D9/OSW12-1310E-Manual.pdf>`_
    """  # noqa E501

    def get_state(self) -> int:
        """State of switch.

        State 1: In 2 -> Out 4 (Bare State)
        State 2: In 2 -> Out 3 (Cross State)

        Returns:
            state -- State of switch (int)

        """
        return int(self.transport.query("S?"))

    @validate_args(state=[1, 2])
    def set_state(self, state: int) -> None:
        """Set state of switch.

        State 1: In 2 -> Out 4 (Bare State)
        State 2: In 2 -> Out 3 (Cross State)

        Arguments:
            state (1 | 2): Which optical path is selected

        """
        self.transport.command(f"S {str(state)}")
        # confirm state
        for _ in range(3):  # 3 attempts
            time.sleep(1)  # wait one second for switch to move
            if self.get_state() == state:
                return  # State change complete, continue.
        final_attempt = self.get_state()
        if final_attempt != state:
            raise Exception(
                f"Could not set state '{state}'! Currently '{final_attempt}'"
            )

    def reset(self) -> None:
        """Reset the switch to default state."""
        self.set_state(1)

    def await_completion(self) -> None:
        """Not implemented."""
        pass

    def get_id(self) -> str:
        """Query the OSW name and the firmware version.

        Returns:
            OSW board name and version.

        """
        return self.transport.query("I?")
