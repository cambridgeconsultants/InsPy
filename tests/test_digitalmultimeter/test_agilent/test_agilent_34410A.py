from collections.abc import Generator

import pytest
from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.digitalmultimeter import DmmAgilent34410A
from inspy.instrument.digitalmultimeter._base import DigitalMultimeter
from inspy.instrument.digitalmultimeter.keysight_dmm import DmmKeysight344xxA
from tests.test_digitalmultimeter.test_digitalmultimeter import DigitMultimeterTest


class TestAgilent34410A(DigitMultimeterTest):
    @fixture(scope="class")
    def dmm(self, address_from_env: str) -> Generator[DigitalMultimeter, None, None]:
        try:
            with DmmAgilent34410A(address_from_env) as _dmm:
                _dmm.reset()
                yield _dmm
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    @pytest.mark.skip("AC filter not properly implemented on 34410A")
    def test_frequency_measurements(self, dmm: DmmKeysight344xxA) -> None:
        """Test M5."""
        pass
