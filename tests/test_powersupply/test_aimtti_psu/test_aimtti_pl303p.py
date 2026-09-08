from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.powersupply._base import PowerSupply
from inspy.instrument.powersupply.aimtti_psu import PsuAimTTIPL303P
from tests.test_powersupply.test_powersupply import PowerSupplyTest


class TestAimttiPL303P(PowerSupplyTest):
    """Note: Untested on Windows USB."""

    @fixture(scope="class")
    def psu(self, address_from_env: str) -> Generator[PowerSupply, None, None]:
        try:
            with PsuAimTTIPL303P(address_from_env) as _psu:
                _psu.reset()
                yield _psu
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_reset(
        self,
        psu: PowerSupply,
        sleep: bool = False,
        sleep_after_reset: bool = False,
        expected_voltage: float = 0.1,
    ) -> None:
        """Test P7."""
        super().test_reset(
            psu,
            sleep=sleep,
            sleep_after_reset=sleep_after_reset,
            expected_voltage=expected_voltage,
        )
