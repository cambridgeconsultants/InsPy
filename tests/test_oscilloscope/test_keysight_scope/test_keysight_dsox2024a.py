from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.oscilloscope import (
    OscilloscopeKeysightDSOX2024A,
)
from inspy.instrument.oscilloscope._base import Oscilloscope
from tests.test_oscilloscope.test_oscilloscope import OscilloscopeTest


class TestKeysightDSOX2024A(OscilloscopeTest):
    @fixture(scope="class")
    def scope(self, address_from_env: str) -> Generator[Oscilloscope, None, None]:
        try:
            with OscilloscopeKeysightDSOX2024A(address_from_env) as _scope:
                _scope.reset()
                yield _scope
        except (VisaIOError, ValueError):
            skip("Instrument not connected")
