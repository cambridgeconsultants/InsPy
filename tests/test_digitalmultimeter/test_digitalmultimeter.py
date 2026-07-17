# Standard library imports
from abc import ABC, abstractmethod
from collections.abc import Generator
from math import isclose

# Library imports
from pytest import fixture, raises

# Internal imports
from inspy.instrument.digitalmultimeter._base import DigitalMultimeter
from inspy.instrument.digitalmultimeter.agilent_dmm import DmmKeysight344xxA


class DigitMultimeterTest(ABC):
    @fixture(scope="class")
    @abstractmethod
    def dmm(self) -> Generator[DigitalMultimeter, None, None]:
        pass

    @fixture(scope="class", autouse=True)
    def print_id(self, dmm: DigitalMultimeter) -> None:
        dmm.logger.info(f"ID: {dmm.get_id()}")

    def _test_measurements(self, dmm: DmmKeysight344xxA) -> None:
        voltage = dmm.measure_voltage()
        current = dmm.measure_current()
        voltage_ac = dmm.measure_voltage_ac()
        current_ac = dmm.measure_current_ac()
        resistance = dmm.measure_resistance()
        resistance_four_wire = dmm.measure_resistance_four_wire()
        temperature = dmm.measure_temperature()
        continuity = dmm.measure_continuity()
        diode_bias = dmm.measure_diode_bias()
        capacitance = dmm.measure_capacitance()
        frequency = dmm.measure_frequency()
        period = dmm.measure_period()

        assert voltage is not None
        assert current is not None
        assert voltage_ac is not None
        assert current_ac is not None
        assert resistance is not None
        assert resistance_four_wire is not None
        assert temperature is not None
        assert continuity is not None
        assert diode_bias is not None
        assert capacitance is not None
        assert frequency is not None
        assert period is not None

        assert isinstance(current, float)
        assert isinstance(voltage_ac, float)
        assert isinstance(current_ac, float)
        assert isinstance(resistance, float)
        assert isinstance(resistance_four_wire, float)
        assert isinstance(temperature, float)
        assert isinstance(continuity, bool)
        assert isinstance(diode_bias, float)
        assert isinstance(capacitance, float)
        assert isinstance(frequency, float)
        assert isinstance(period, float)

    def test_measurements(self, dmm: DmmKeysight344xxA) -> None:
        """Test M1."""
        self._test_measurements(dmm)

    def _test_set_trace_function(self, dmm: DigitalMultimeter) -> None:
        dmm.set_sampling_measurement_mode(function="CURR:AC")
        assert dmm.get_sampling_measurement_mode() == "CURR:AC"
        dmm.reset()
        assert dmm.get_sampling_measurement_mode() == "VOLT"

    def test_set_trace_function(self, dmm: DigitalMultimeter) -> None:
        """Test M2."""
        self._test_set_trace_function(dmm)

    def _test_trace_function(self, dmm: DmmKeysight344xxA) -> None:
        dmm.set_sampling_measurement_mode(function="VOLT")
        dmm.set_trigger_immediate()
        dmm.set_sample_points(sample_points=5)
        dmm.set_sample_interval(sample_interval=2)
        dmm.set_measurement_range(measurement_range=1)
        dmm.set_averaging_time(averaging_time=0.5)

        dmm.set_trigger_delay(trigger_delay=0.5)
        dmm.set_wait_for_trigger()
        samples = dmm.get_samples()
        assert len(samples) == 5
        assert dmm.get_sampling_measurement_mode() == "VOLT"
        assert dmm.get_trigger_source() == "IMM"
        assert dmm.get_sample_points() == 5
        assert isclose(dmm.get_sample_interval(), 2, abs_tol=1e-3)
        assert isclose(dmm.get_averaging_time(), 0.5, abs_tol=1e-3)
        assert dmm.get_measurement_range() == 1
        assert isclose(dmm.get_trigger_delay(), 0.5, abs_tol=1e-3)

    def test_trace_function(self, dmm: DmmKeysight344xxA) -> None:
        """Test M3."""
        self._test_trace_function(dmm)

    def _test_exception(self, dmm: DigitalMultimeter) -> None:
        dmm.set_sampling_measurement_mode(function="CAP")
        with raises(Exception) as _:
            dmm.set_averaging_time(averaging_time=1)

    def test_exception(self, dmm: DigitalMultimeter) -> None:
        """Test M4."""
        self._test_exception(dmm)

    def _test_frequency_measurements(self, dmm: DmmKeysight344xxA) -> None:
        dmm.set_measure_frequency_bandwidth(bandwidth=3)
        frequency = dmm.measure_frequency()
        period = dmm.measure_period()

        assert dmm.get_measure_frequency_bandwidth() == 3
        assert frequency is not None
        assert period is not None

    def test_frequency_measurements(self, dmm: DmmKeysight344xxA) -> None:
        """Test M5."""
        self._test_frequency_measurements(dmm)
