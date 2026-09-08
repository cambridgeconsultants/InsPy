from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.oscilloscope import OscilloscopeKeysightDSOX1102G
from inspy.instrument.oscilloscope._base import Oscilloscope
from inspy.instrument.oscilloscope.keysight_oscilloscope import OscilloscopeKeysightBase
from tests.test_oscilloscope.test_oscilloscope import OscilloscopeTest


class TestKeysightDSOX1102G(OscilloscopeTest):
    @fixture(scope="class")
    def scope(self, address_from_env: str) -> Generator[Oscilloscope, None, None]:
        try:
            with OscilloscopeKeysightDSOX1102G(address_from_env) as _scope:
                _scope.reset()
                yield _scope
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_wavegen_square(
        self,
        scope: OscilloscopeKeysightBase,
        measure_counter: bool = False,
        measure_pre_shoot: bool = False,
        extra_measurements: bool = False,
    ) -> None:
        """Test O9."""
        super().test_wavegen_square(scope, extra_measurements=extra_measurements)
