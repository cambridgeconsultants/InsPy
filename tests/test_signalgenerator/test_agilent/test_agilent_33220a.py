from collections.abc import Generator

from pytest import fixture, skip
from pyvisa.errors import VisaIOError

from inspy.instrument.signalgenerator._base import SignalGenerator
from inspy.instrument.signalgenerator.agilent_siggen import SigGenAgilent33220A
from tests.test_signalgenerator.test_signalgenerator import SignalGeneratorTest


class TestAgilent33220A(SignalGeneratorTest):
    @fixture(scope="function")
    def siggen(self, address_from_env: str) -> Generator[SignalGenerator, None, None]:
        try:
            with SigGenAgilent33220A(address_from_env) as _siggen:
                _siggen.reset()
                yield _siggen
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    arb_mode = "USER"
    num_supported_waveforms = 4
    waveform_modes = ["SINE", "SQUARE", "RAMP", "PULSE", "NOISE", "DC"]
