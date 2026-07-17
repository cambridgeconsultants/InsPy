from collections.abc import Generator

import pytest
from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.oscilloscope import (
    OscilloscopeAgilentDSO6012A,
)
from inspy.instrument.oscilloscope._base import Oscilloscope
from inspy.instrument.oscilloscope.keysight_oscilloscope import OscilloscopeKeysightBase
from tests.test_oscilloscope.test_oscilloscope import OscilloscopeTest


class TestAgilentDSO6012A(OscilloscopeTest):
    probe_compensation_frequency: float = 1200.0

    @fixture(scope="class")
    def scope(self, address_from_env: str) -> Generator[Oscilloscope, None, None]:
        try:
            with OscilloscopeAgilentDSO6012A(address_from_env) as _scope:
                _scope.reset()
                yield _scope
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    def test_get_screenshot(self, scope: Oscilloscope) -> None:
        """Test O8."""
        super()._test_get_screenshot(scope, width=1024, height=829)

    @pytest.mark.skip("Not implemented on Agilent DSO6012A")
    def test_wavegen_square(self, scope: OscilloscopeKeysightBase) -> None:
        """Test O9."""
        pass

    @pytest.mark.skip("Not implemented on Agilent DSO6012A")
    def test_wavegen(self, scope: Oscilloscope) -> None:
        """Test O10."""
        pass
