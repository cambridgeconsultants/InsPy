from collections.abc import Generator

from pytest import fixture, skip
from serial import SerialException

from inspy.instrument.switch import OpticalSwitchThorlabsOSW12


class TestOpticalSwitchThorLabsOSW12:
    """Note: Untested on Windows USB."""

    @fixture(scope="class")
    def switch(
        self, address_from_env: str
    ) -> Generator[OpticalSwitchThorlabsOSW12, None, None]:
        if address_from_env == "UNSET":
            skip("No address provided")
        try:
            with OpticalSwitchThorlabsOSW12(address_from_env) as _switch:
                _switch.reset()
                yield _switch
        except SerialException:
            skip("Instrument not connected")

    def test_set_state(self, switch: OpticalSwitchThorlabsOSW12) -> None:
        switch.set_state(1)
        assert switch.get_state() == 1

        switch.reset()

        switch.set_state(2)
        assert switch.get_state() == 2

        switch.reset()

        switch.set_state(1)
        assert switch.get_state() == 1

    def test_reset(self, switch: OpticalSwitchThorlabsOSW12) -> None:
        switch.set_state(2)
        assert switch.get_state() == 2
        switch.reset()
        assert switch.get_state() == 1

    def test_id(self, switch: OpticalSwitchThorlabsOSW12) -> None:
        assert switch.get_id().startswith("OSW1x2 Optical Switch V")
