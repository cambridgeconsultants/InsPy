import time
from abc import ABC, abstractmethod
from collections.abc import Generator

from pytest import approx, fixture

# Library imports
from inspy.instrument.powersupply import aimtti_psu, keysight_psu

# Internal imports
from inspy.instrument.powersupply._base import PowerSupply


class PowerSupplyTest(ABC):
    @fixture(scope="class")
    @abstractmethod
    def psu(self) -> Generator[PowerSupply, None, None]:
        pass

    @fixture(scope="class", autouse=True)
    def print_id(self, psu: PowerSupply) -> None:
        psu.logger.info(f"ID: {psu.get_id()}")

    PowerSupplyWithTrip = aimtti_psu.PsuAimTTiBase | keysight_psu.PsuKeysightBase

    def test_set_get_channel_state(self, psu: PowerSupply) -> None:
        """Test P1."""
        for test_channel in psu.channels:
            time.sleep(0.5)
            psu.set_channel_state(channel=test_channel, enable=True)
            psu.await_completion()
            time.sleep(0.5)
            assert psu.get_channel_state(channel=test_channel) is True

            time.sleep(0.5)
            psu.set_channel_state(channel=test_channel, enable=False)
            psu.await_completion()
            time.sleep(0.5)
            assert psu.get_channel_state(channel=test_channel) is False

    def test_set_get_voltage(self, psu: PowerSupply) -> None:
        """Test P2."""
        test_voltage = 1
        for test_channel in psu.channels:
            psu.set_voltage(voltage=test_voltage, channel=test_channel)
            psu.await_completion()
            time.sleep(0.5)
            assert psu.get_voltage(channel=test_channel) == test_voltage

    def test_set_get_current(self, psu: PowerSupply) -> None:
        """Test P3."""
        test_current = 1
        for test_channel in psu.channels:
            psu.set_current(current=test_current, channel=test_channel)
            psu.await_completion()
            time.sleep(0.5)
            assert psu.get_current(channel=test_channel) == test_current

    def test_measure_voltage_after_channel_set(
        self, psu: PowerSupply, sleep_between_runs: bool = True
    ) -> None:
        """Test P4."""
        test_voltage = 3
        for test_channel in psu.channels:
            psu.set_voltage(voltage=test_voltage, channel=test_channel)
            psu.set_channel_state(channel=test_channel)
            psu.await_completion()
            if sleep_between_runs:
                time.sleep(0.5)
            assert psu.measure_voltage(channel=test_channel) == approx(
                test_voltage, rel=0.1
            )

    def test_set_output_voltage_trip_point(
        self,
        psu: PowerSupplyWithTrip,
        voltage: float = 20,
        sleep_between_runs: bool = True,
    ) -> None:
        """Test P5."""
        test_voltage = voltage
        for test_channel in psu.channels:
            psu.set_output_voltage_trip_point(
                voltage=test_voltage, channel=test_channel
            )
            psu.await_completion()
            if sleep_between_runs:
                time.sleep(0.5)
            assert (
                psu.get_output_voltage_trip_point(channel=test_channel) == test_voltage
            )
        psu.reset()

    def test_set_output_current_trip_point(self, psu: aimtti_psu.PsuAimTTiBase) -> None:
        """Test P6."""
        test_current = 0.5
        for test_channel in psu.channels:
            psu.set_output_current_trip_point(
                current=test_current, channel=test_channel
            )
            psu.await_completion()
            time.sleep(0.5)
            assert (
                psu.get_output_current_trip_point(channel=test_channel) == test_current
            )
        psu.reset()

    def test_reset(
        self,
        psu: PowerSupply,
        sleep: bool = True,
        sleep_after_reset: bool = False,
        expected_voltage: float = 0,
    ) -> None:
        """Test P7."""
        psu.set_voltage(voltage=1)
        psu.set_channel_state()
        psu.await_completion()

        if sleep and not sleep_after_reset:
            time.sleep(0.5)
        psu.reset()
        if sleep and sleep_after_reset:
            time.sleep(0.5)

        assert psu.get_channel_state() is False
        assert psu.get_voltage() == expected_voltage
