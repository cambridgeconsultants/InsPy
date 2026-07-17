from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.oscilloscope import OscilloscopeKeysightDSOX1202G
from inspy.instrument.oscilloscope._base import Oscilloscope
from inspy.instrument.oscilloscope.keysight_oscilloscope import OscilloscopeKeysightBase
from tests.test_oscilloscope.test_oscilloscope import OscilloscopeTest


class TestKeysightDSOX1202G(OscilloscopeTest):
    @fixture(scope="class")
    def scope(self, address_from_env: str) -> Generator[Oscilloscope, None, None]:
        try:
            with OscilloscopeKeysightDSOX1202G(address_from_env) as _scope:
                _scope.reset()
                yield _scope
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_wavegen_square(self, scope: OscilloscopeKeysightBase) -> None:
        """Test O9."""
        super()._test_wavegen_square(
            scope, measure_counter=True, measure_pre_shoot=True
        )
