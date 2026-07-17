from collections.abc import Generator

import pytest
from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.digitalmultimeter import DmmKeysight34461A
from inspy.instrument.digitalmultimeter._base import DigitalMultimeter
from inspy.instrument.digitalmultimeter.keysight_dmm import DmmKeysight344xxA
from tests.test_digitalmultimeter.test_digitalmultimeter import DigitMultimeterTest


class TestKeysight34461A(DigitMultimeterTest):
    @fixture(scope="class")
    def dmm(self, address_from_env: str) -> Generator[DigitalMultimeter, None, None]:
        try:
            with DmmKeysight34461A(address_from_env) as _dmm:
                _dmm.reset()
                yield _dmm
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    @pytest.mark.skip("Function set_sample_interval not supported on 34461A")
    def test_trace_function(self, dmm: DmmKeysight344xxA) -> None:
        """Test M3."""
        pass
