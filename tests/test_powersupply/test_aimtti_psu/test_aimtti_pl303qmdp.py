import time
from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.powersupply._base import PowerSupply
from inspy.instrument.powersupply.aimtti_psu import PsuAimTTiPL303QMDP
from tests.test_powersupply.test_powersupply import PowerSupplyTest


class TestAimttiPL303QMDP(PowerSupplyTest):
    @fixture(scope="class")
    def psu(self, address_from_env: str) -> Generator[PowerSupply, None, None]:
        try:
            with PsuAimTTiPL303QMDP(address_from_env) as _psu:
                _psu.reset()
                yield _psu
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_reset(self, psu: PowerSupply) -> None:
        """Test P7."""
        super()._test_reset(psu, sleep=False, expected_voltage=0.1)

    def test_set_get_current_range(self, psu: PsuAimTTiPL303QMDP) -> None:
        test_current_range = "High"
        for test_channel in [1, 2]:
            psu.set_current_range(
                current_range=test_current_range, channel=test_channel
            )
            psu.await_completion()
            time.sleep(0.5)
            assert psu.get_current_range(channel=test_channel) == test_current_range
        psu.reset()
