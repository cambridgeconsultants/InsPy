import time
from collections.abc import Generator

import numpy as np
import pytest
from pytest import fixture, raises, skip
from pyvisa.errors import VisaIOError
from scipy.signal import sawtooth, square

from inspy.instrument.signalgenerator._base import SignalGenerator
from inspy.instrument.signalgenerator.keysight_siggen import SigGenKeysight33522B
from tests.test_signalgenerator.test_signalgenerator import SignalGeneratorTest


class TestKeysight33522B(SignalGeneratorTest):
    @fixture(scope="function")
    def siggen(self, address_from_env: str) -> Generator[SignalGenerator, None, None]:
        try:
            with SigGenKeysight33522B(address_from_env) as _siggen:
                _siggen.reset()
                yield _siggen
        except (VisaIOError, ValueError):
            skip("Instrument not connected")

    waveform_modes = [
        "SINE",
        "SQUARE",
        "RAMP",
        "PULSE",
        "NOISE",
        "TRIANGLE",
        "PRBS",
        "DC",
    ]

    @pytest.mark.skip("Not implemented")
    def test_delete_saved_user_waveform(
        self, siggen: SignalGeneratorTest.SigGenWithDelete
    ) -> None:
        """Test S14."""
        pass

    def test_save_waveform_name_exists(
        self, siggen: SignalGeneratorTest.SigGenWithDelete
    ) -> None:
        """Test S15."""
        waveform = []

        t = np.linspace(0, 1, 200)
        waves = [
            0.5 * square(2 * np.pi * 3 * t),
            0.3 * sawtooth(2 * np.pi * 2 * t),
        ]
        waveform = sum(waves)
        siggen.set_channel_state(channel=1, enable=True)
        siggen.set_new_arbitrary_waveform(array=waveform, name=self.arb_name, channel=1)
        siggen.set_voltage_amplitude(voltage=5.0, channel=1)
        siggen.set_voltage_offset(voltage=1.0, channel=1)
        time.sleep(0.5)
        assert siggen.get_saved_user_waveforms(channel=1) == [self.arb_name]

        with raises(ValueError):
            siggen.set_new_arbitrary_waveform(
                array=waveform, name=self.arb_name, channel=1
            )
        time.sleep(0.5)
        assert siggen.get_saved_user_waveforms(channel=1) == [self.arb_name]

        # There is no direct command to delete a particular waveform for this
        # signal generator
        siggen.delete_all_saved_user_waveforms(channel=1)
        time.sleep(0.5)
        assert siggen.get_saved_user_waveforms(channel=1) == []
