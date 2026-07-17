from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.digitalmultimeter import DmmKeysight34465A
from inspy.instrument.digitalmultimeter._base import DigitalMultimeter
from tests.test_digitalmultimeter.test_digitalmultimeter import DigitMultimeterTest


class TestKeysight34465A(DigitMultimeterTest):
    @fixture(scope="class")
    def dmm(self, address_from_env: str) -> Generator[DigitalMultimeter, None, None]:
        try:
            with DmmKeysight34465A(address_from_env) as _dmm:
                _dmm.reset()
                yield _dmm
        except (VisaIOError, ValueError):
            skip("Instrument not connected")
