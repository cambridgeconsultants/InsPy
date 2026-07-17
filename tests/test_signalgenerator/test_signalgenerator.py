# Standard library imports
import time
from abc import ABC, abstractmethod
from collections.abc import Generator

import numpy as np
from pytest import fixture, raises
from scipy.signal import sawtooth, square

from inspy.instrument.signalgenerator import (
    agilent_siggen,
    hp_siggen,
    keysight_siggen,
)

# Internal imports
from inspy.instrument.signalgenerator._base import SignalGenerator


class SignalGeneratorTest(ABC):
    @fixture(scope="function")
    @abstractmethod
    def siggen(self) -> Generator[SignalGenerator, None, None]:
        pass

    @fixture(scope="function", autouse=True)
    def print_id(self, siggen: SignalGenerator) -> None:
        siggen.logger.info(f"ID: {siggen.get_id()}")

    SigGenWithDelete = agilent_siggen.SigGenAgilentBase | hp_siggen.SigGenHPBase
    SigGenWithSave = (
        agilent_siggen.SigGenAgilentBase
        | hp_siggen.SigGenHPBase
        | keysight_siggen.SigGenKeysightBase
    )

    arb_mode = "ARB"
    arb_name = "USERFUNC"
    num_supported_waveforms = 5
    waveform_modes = ["SINE", "SQUARE", "RAMP", "PULSE", "NOISE"]

    def test_set_get_channel_state(self, siggen: SignalGenerator) -> None:
        """Test S1."""
        for channel in siggen.channels:
            siggen.set_channel_state(channel=channel, enable=True)
            time.sleep(0.5)
            assert siggen.get_channel_state(channel=channel) is True

            siggen.set_channel_state(channel=channel, enable=False)
            time.sleep(0.5)
            assert siggen.get_channel_state(channel=channel) is False

    def test_set_get_frequency(self, siggen: SignalGenerator) -> None:
        """Test S2."""
        test_frequencies = [1000, 2000, 3000, 4000, 5000]

        for test_frequency in test_frequencies:
            for channel in siggen.channels:
                siggen.set_frequency(frequency=test_frequency, channel=channel)
                time.sleep(0.5)
                assert siggen.get_frequency(channel=channel) == test_frequency

    def test_set_get_voltage_low(self, siggen: SignalGenerator) -> None:
        """Test S3."""
        test_voltage = -1

        for channel in siggen.channels:
            siggen.set_voltage_low(voltage=test_voltage, channel=channel)
            time.sleep(0.5)
            assert siggen.get_voltage_low(channel=channel) == test_voltage

    def test_set_get_voltage_high(self, siggen: SignalGenerator) -> None:
        """Test S4."""
        test_voltage = 1

        for channel in siggen.channels:
            siggen.set_voltage_high(voltage=test_voltage, channel=channel)
            time.sleep(0.5)
            assert siggen.get_voltage_high(channel=channel) == test_voltage

    def test_set_get_voltage_amplitude(self, siggen: SignalGenerator) -> None:
        """Test S5."""
        test_voltage = 1

        for channel in siggen.channels:
            siggen.set_voltage_amplitude(voltage=test_voltage, channel=channel)
            time.sleep(0.5)
            assert siggen.get_voltage_amplitude(channel=channel) == test_voltage

    def test_set_get_voltage_offset(self, siggen: SignalGenerator) -> None:
        """Test S6."""
        test_voltage = 1

        for channel in siggen.channels:
            siggen.set_voltage_amplitude(voltage=test_voltage * 2.5, channel=channel)
            siggen.set_voltage_offset(voltage=test_voltage, channel=channel)
            time.sleep(0.5)
            assert siggen.get_voltage_offset(channel=channel) == test_voltage

    def test_set_get_impedance_low(self, siggen: SignalGenerator) -> None:
        """Test S7."""
        test_impedance = "50"

        for channel in siggen.channels:
            siggen.set_impedance(impedance=test_impedance, channel=channel)
            time.sleep(0.5)
            assert siggen.get_impedance(channel=channel) == test_impedance

    def test_set_get_impedance_high(self, siggen: SignalGenerator) -> None:
        """Test S8."""
        test_impedance = "HIGH"

        for channel in siggen.channels:
            siggen.set_impedance(impedance=test_impedance, channel=channel)
            time.sleep(0.5)
            assert siggen.get_impedance(channel=channel) == test_impedance

    def test_set_get_waveform_modes(self, siggen: SignalGenerator) -> None:
        """Test S9."""
        for channel in siggen.channels:
            siggen.set_channel_state(channel=channel, enable=True)
            for waveform in self.waveform_modes:
                siggen.set_waveform_mode(mode=waveform, channel=channel)
                time.sleep(0.5)
                assert siggen.get_waveform_mode(channel=channel) == waveform
                time.sleep(0.5)

    def test_reset(self, siggen: SignalGenerator) -> None:
        """Test S10."""
        for channel in siggen.channels:
            assert siggen.get_channel_state(channel=channel) is False
            assert siggen.get_frequency(channel=channel) == 1000
            assert siggen.get_voltage_low(channel=channel) == -0.05
            assert siggen.get_voltage_high(channel=channel) == 0.05
            assert siggen.get_voltage_amplitude(channel=channel) == 0.1
            assert siggen.get_voltage_offset(channel=channel) == 0
            assert siggen.get_impedance(channel=channel) == "50"
            assert siggen.get_waveform_mode(channel=channel) == "SINE"

    def test_set_get_waveform(self, siggen: SignalGenerator) -> None:
        """Test S11."""
        waveform = []

        t = np.linspace(0, 1, 1000)
        waves = [
            0.5 * square(2 * np.pi * 3 * t),
            0.3 * sawtooth(2 * np.pi * 2 * t),
        ]
        waveform = sum(waves)

        siggen.set_channel_state(channel=1, enable=True)
        siggen.set_new_arbitrary_waveform(
            array=waveform,
            name=self.arb_name,
            channel=1,
        )
        time.sleep(0.5)
        assert siggen.get_waveform_mode(channel=1) == self.arb_mode

    def test_add_multiple_waveforms(self, siggen: SigGenWithSave) -> None:
        """Test S12."""
        waveform = []

        t = np.linspace(0, 1, 1000)
        waves = [
            0.5 * square(2 * np.pi * 3 * t),
            0.3 * sawtooth(2 * np.pi * 2 * t),
        ]
        waveform = sum(waves)

        siggen.set_channel_state(channel=1, enable=True)
        for i in range(self.num_supported_waveforms):
            name = f"ARB{i}"
            siggen.set_new_arbitrary_waveform(array=waveform, name=name, channel=1)
            assert name in siggen.get_saved_user_waveforms(channel=1)

    def test_get_saved_user_waveforms(self, siggen: SigGenWithSave) -> None:
        """Test S13."""
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

    def test_delete_saved_user_waveform(self, siggen: SigGenWithDelete) -> None:
        """Test S14."""
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

        siggen.delete_saved_user_waveform(name=self.arb_name)
        time.sleep(0.5)
        assert siggen.get_saved_user_waveforms(channel=1) == []

    def test_save_waveform_name_exists(self, siggen: SigGenWithDelete) -> None:
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

        siggen.delete_saved_user_waveform(name=self.arb_name)
        time.sleep(0.5)
        assert siggen.get_saved_user_waveforms(channel=1) == []
