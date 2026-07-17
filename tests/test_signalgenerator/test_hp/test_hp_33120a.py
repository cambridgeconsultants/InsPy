import time
from collections.abc import Generator

from pytest import fixture, skip
from serial import SerialException

from inspy.instrument.signalgenerator._base import SignalGenerator
from inspy.instrument.signalgenerator.hp_siggen import SigGenHP33120A
from tests.test_signalgenerator.test_signalgenerator import SignalGeneratorTest


class TestHP33120A(SignalGeneratorTest):
    arb_mode = "USER"
    arb_name = "USERFUNC"
    num_supported_waveforms = 4
    waveform_modes = ["SINE", "SQUARE", "RAMP", "NOISE", "DC"]

    @fixture(scope="function")
    def siggen(self, address_from_env: str) -> Generator[SignalGenerator, None, None]:
        try:
            with SigGenHP33120A(address_from_env) as _siggen:
                _siggen.reset()
                yield _siggen
        except (SerialException, ValueError):
            skip("Instrument not connected")

    def test_set_get_channel_state(self, siggen: SignalGenerator) -> None:
        """Test S1.

        The 33120A output is always on and has no ``OUTPut[:STATe]`` command, so
        the output cannot be toggled off and this test does not apply.
        """
        skip("The HP 33120A output is always on; it cannot be enabled/disabled.")

    def test_set_get_voltage_low(self, siggen: SignalGenerator) -> None:
        """Test S3.

        The 33120A sets levels via amplitude + offset only; it has no low/high
        voltage commands, so this test does not apply.
        """
        skip("The HP 33120A has no low voltage command (uses amplitude/offset).")

    def test_set_get_voltage_high(self, siggen: SignalGenerator) -> None:
        """Test S4.

        The 33120A sets levels via amplitude + offset only; it has no low/high
        voltage commands, so this test does not apply.
        """
        skip("The HP 33120A has no high voltage command (uses amplitude/offset).")

    def test_reset(self, siggen: SignalGenerator) -> None:
        """Test S10.

        The generic reset test asserts the output is off and checks the low/high
        voltage defaults, neither of which applies to the 33120A (output is always
        on; levels are amplitude/offset). This override checks the *RST defaults
        that the 33120A does support.
        """
        siggen.reset()
        time.sleep(0.5)
        for channel in siggen.channels:
            assert siggen.get_frequency(channel=channel) == 1000
            assert siggen.get_voltage_amplitude(channel=channel) == 0.1
            assert siggen.get_voltage_offset(channel=channel) == 0
            assert siggen.get_impedance(channel=channel) == "50"
            assert siggen.get_waveform_mode(channel=channel) == "SINE"
