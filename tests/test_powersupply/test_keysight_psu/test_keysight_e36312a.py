import time
from collections.abc import Generator

import pytest
from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.powersupply._base import PowerSupply
from inspy.instrument.powersupply.keysight_psu import PsuKeysightE36312A
from tests.test_powersupply.test_powersupply import PowerSupplyTest


class TestKeysightE36312A(PowerSupplyTest):
    @fixture(scope="class")
    def psu(self, address_from_env: str) -> Generator[PowerSupply, None, None]:
        try:
            with PsuKeysightE36312A(address_from_env) as _psu:
                _psu.reset()
                yield _psu
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_measure_voltage_after_channel_set(
        self, psu: PowerSupply, sleep_between_runs: bool = False
    ) -> None:
        """Test P4."""
        super().test_measure_voltage_after_channel_set(
            psu, sleep_between_runs=sleep_between_runs
        )

    def test_set_output_voltage_trip_point(
        self,
        psu: PowerSupplyTest.PowerSupplyWithTrip,
        voltage: float = 5.1,
        sleep_between_runs: bool = False,
    ) -> None:
        """Test P5."""
        super().test_set_output_voltage_trip_point(
            psu, voltage=voltage, sleep_between_runs=sleep_between_runs
        )

    @pytest.mark.skip("Not implemented")
    def test_set_output_current_trip_point(self, psu: PowerSupply) -> None:
        """Test P6."""
        pass

    def test_reset(
        self,
        psu: PowerSupply,
        sleep: bool = False,
        sleep_after_reset: bool = False,
        expected_voltage: float = 0,
    ) -> None:
        """Test P7."""
        super().test_reset(
            psu,
            sleep=sleep,
            sleep_after_reset=sleep_after_reset,
            expected_voltage=expected_voltage,
        )

    def test_reset_voltage_trip_disable_channel(self, psu: PsuKeysightE36312A) -> None:
        psu.set_output_voltage_trip_point(voltage=5)
        psu.set_voltage(voltage=6)
        psu.set_channel_state(True)
        time.sleep(0.5)
        assert psu.get_voltage_trip_status() is True
        psu.reset_voltage_trip_with_disable()
        assert psu.get_voltage_trip_status() is False

    def test_reset_current_trip_disable_channel(self, psu: PsuKeysightE36312A) -> None:
        psu.set_voltage(voltage=6)
        psu.set_current(current=0.002)
        psu.set_current_protection_state()
        psu.set_channel_state(True)
        time.sleep(0.5)
        assert psu.get_current_trip_status() is True
        psu.reset_current_trip_with_disable()
        assert psu.get_current_trip_status() is False
