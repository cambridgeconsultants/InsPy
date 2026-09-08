"""Test oscilloscope.

The scope should be configured as follows:

Channel 1:
A standard x10 scope probe clipped on to the probe compensation pin, the ground clip
should be connected to the ground pin (next to the probe compensation pin).

Channel 2:
If the oscilloscope has a waveform generator a BNC cable should be connected to the Gen
Out connector.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import Generator
from io import BytesIO
from math import sqrt

import PIL.Image
from pytest import approx, fixture, raises
from pyvisa.errors import VisaIOError

from inspy.instrument.oscilloscope._base import Oscilloscope, OscilloscopeError
from inspy.instrument.oscilloscope.agilent_oscilloscope import OscilloscopeAgilentBase
from inspy.instrument.oscilloscope.keysight_oscilloscope import OscilloscopeKeysightBase

AgilentAndKeysightBase = OscilloscopeAgilentBase | OscilloscopeKeysightBase


class OscilloscopeTest(ABC):
    probe_compensation_amplitude: float = 2.5
    probe_compensation_frequency: float = 1e3

    @fixture(scope="class")
    @abstractmethod
    def scope(self) -> Generator[Oscilloscope, None, None]:
        pass

    @fixture(scope="class", autouse=True)
    def print_id(self, scope: AgilentAndKeysightBase) -> None:
        scope.logger.info(f"ID: {scope.get_id()}")

    def test_measure_freq_amp_normal(self, scope: AgilentAndKeysightBase) -> None:
        """Test O1."""
        channel = 1
        coupling = "AC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = 0.0
        voltage_range = 5.0
        time_range = 10e-3
        trigger_level = 0.0
        trigger_hold_off = 0.9

        scope.set_timebase(timebase_range=time_range, reference="CENT")
        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )

        scope.set_trigger(
            channel=channel,
            level=trigger_level,
            slope="POS",
            sweep="NORM",
            coupling=coupling,
            mode="EDGE",
            noise_reject=True,
            hold_off=trigger_hold_off,
        )

        assert scope.get_timebase_range() == time_range
        assert scope.get_timebase_reference() == "CENT"
        assert scope.get_channel_range(channel) == approx(voltage_range, rel=0.01)
        assert scope.get_channel_attenuation(channel) == attenuation
        assert scope.get_channel_offset(channel) == offset
        assert scope.get_channel_coupling(channel) == coupling
        assert scope.get_channel_attenuation(channel) == attenuation
        assert scope.get_channel_bw_limit(channel) == bw_limit
        assert scope.get_channel_state(channel) is True
        assert scope.get_trigger_sweep() == "NORM"
        assert scope.get_trigger_mode() == "EDGE"
        assert scope.get_trigger_coupling() == coupling
        assert scope.get_trigger_edge_source() == channel
        assert scope.get_trigger_edge_level() == trigger_level
        assert scope.get_trigger_slope() == "POS"
        assert scope.get_trigger_noise_reject() is True
        assert scope.get_trigger_hold_off() == trigger_hold_off

        scope.digitize()
        assert scope.get_measurement_frequency(channel) == approx(
            self.probe_compensation_frequency, rel=0.1
        )
        assert scope.get_measurement_amplitude(channel) == approx(
            self.probe_compensation_amplitude, rel=0.2
        )

    def test_trigger_forced(self, scope: AgilentAndKeysightBase) -> None:
        """Test O2."""
        channel = 1
        coupling = "AC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = 0.0
        voltage_range = 5.0
        time_range = 10e-3

        scope.set_timebase(timebase_range=time_range, reference="CENT")
        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )
        scope.trigger_now()
        assert scope.get_measurement_frequency(channel) == approx(
            self.probe_compensation_frequency, rel=0.1
        )
        assert scope.get_measurement_amplitude(channel) == approx(
            self.probe_compensation_amplitude, rel=0.1
        )

    def test_trigger_out_of_range(self, scope: AgilentAndKeysightBase) -> None:
        """Test O3."""
        channel = 1
        coupling = "AC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = 0.0
        voltage_range = 5.0
        trigger_level = 15.0

        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )
        with raises(OscilloscopeError):
            scope.set_trigger(
                channel=channel,
                level=trigger_level,
                slope="POS",
                sweep="NORM",
                coupling=coupling,
                mode="EDGE",
            )

    def test_trigger_timeout(self, scope: AgilentAndKeysightBase) -> None:
        """Test O4."""
        channel = 1
        coupling = "AC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = 0.0
        voltage_range = 5.0
        time_range = 10e-3
        # Trigger deliberately above the (AC-coupled, ~+-1.25 V) signal so it
        # never fires and digitize times out. It must still be within the
        # channel's valid trigger range - roughly +-1.5x the half voltage_range,
        # i.e. ~+-3.78 V here - otherwise set_trigger raises -222 Data out of
        # range before digitize is reached.
        trigger_level = 3.0

        scope.set_timebase(timebase_range=time_range, reference="CENT")
        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )
        scope.set_trigger(
            channel=channel,
            level=trigger_level,
            slope="POS",
            sweep="NORM",
            coupling=coupling,
            mode="EDGE",
        )

        with raises((VisaIOError, ValueError)):
            scope.digitize()

    def test_trigger_auto(self, scope: AgilentAndKeysightBase) -> None:
        """Test O5."""
        channel = 1
        coupling = "AC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = 0.0
        voltage_range = 5.0
        time_range = 10e-3
        trigger_level = 0.0

        scope.set_timebase(timebase_range=time_range, reference="CENT")
        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )
        scope.set_trigger(
            channel=channel,
            level=trigger_level,
            slope="POS",
            sweep="AUTO",
            coupling=coupling,
            mode="EDGE",
        )

        scope.digitize()
        assert scope.get_measurement_frequency(channel) == approx(
            self.probe_compensation_frequency, rel=0.1
        )
        assert scope.get_measurement_amplitude(channel) == approx(
            self.probe_compensation_amplitude, rel=0.2
        )

    def test_get_waveform(self, scope: AgilentAndKeysightBase) -> None:
        """Test O6."""
        channel = 1
        coupling = "DC"
        bw_limit = True
        attenuation = 10.0  # 10x probe
        offset = self.probe_compensation_amplitude / 2
        voltage_range = 5.0
        time_range = 10e-3
        # Trigger mid-signal so the NORM-sweep edge reliably fires. The demo
        # signal is DC-coupled ~0..amplitude, so level 0.0 sits at its bottom
        # edge and often never crosses going positive, leaving digitize to time
        # out.
        trigger_level = self.probe_compensation_amplitude / 2
        max_rms_error = 2.0

        scope.set_timebase(timebase_range=time_range, reference="CENT")
        scope.set_channel(
            channel=channel,
            voltage_range=voltage_range,
            offset=offset,
            coupling=coupling,
            attenuation=attenuation,
            bw_limit=bw_limit,
            state=True,
        )
        scope.set_trigger(
            channel=channel,
            level=trigger_level,
            slope="POS",
            sweep="NORM",
            coupling=coupling,
            mode="EDGE",
        )
        scope.digitize()
        times, voltages = scope.get_waveform(channel)
        amp = self.probe_compensation_amplitude
        period = 1.0 / self.probe_compensation_frequency
        expected = [amp * ((t % period) < (0.5 * period)) for t in times]
        error = [(v - e) ** 2 for v, e in zip(voltages, expected, strict=True)]
        assert times[-1] - times[0] == approx(time_range, rel=0.01)
        assert sqrt(sum(error) / len(error)) < max_rms_error

    def test_setup(self, scope: AgilentAndKeysightBase) -> None:
        """Test O7."""
        scope.set_timebase(timebase_range=0.5)
        initial_setup = scope.get_setup()
        scope.set_timebase(timebase_range=2.0)
        assert initial_setup != scope.get_setup()
        scope.set_setup(initial_setup)
        assert initial_setup == scope.get_setup()

    def test_get_screenshot(
        self, scope: Oscilloscope, width: int = 800, height: int = 503
    ) -> None:
        """Test O8."""
        im = PIL.Image.open(BytesIO(scope.get_screenshot()))
        assert im.size == (width, height)

    def test_wavegen_square(
        self,
        scope: OscilloscopeKeysightBase,
        measure_counter: bool = False,
        measure_pre_shoot: bool = False,
        extra_measurements: bool = True,
    ) -> None:
        """Test O9."""
        vmax = 3.3
        vmin = 0.0
        duty = 0.4
        nduty = 1 - duty
        frequency = 1e3
        scope.set_wavegen(
            function="SQU",
            frequency=frequency,
            voltage_high=vmax,
            voltage_low=vmin,
            duty_cycle=duty,
            output_impedance="ONEM",
        )
        scope.set_wavegen_output_enable(True)

        channel = 2
        scope.set_timebase(timebase_range=10e-3, reference="LEFT")
        scope.set_channel(
            channel=channel,
            voltage_range=5,
            attenuation=1.0,
            offset=(vmax + vmin) / 2.0,
            bw_limit=True,
            coupling="DC",
        )
        scope.set_trigger(
            channel=channel,
            level=(vmax + vmin) / 2.0,
            slope="POS",
            sweep="NORM",
            coupling="DC",
            mode="EDGE",
        )

        scope.digitize()

        assert scope.get_measurement_amplitude(channel) == approx(vmax, abs=0.2)
        assert scope.get_measurement_duty_cycle(channel) == approx(duty, rel=0.1)
        assert scope.get_measurement_frequency(channel) == approx(frequency, rel=0.1)
        assert scope.get_measurement_positive_pulse_width(channel) == approx(
            duty / frequency, rel=0.1
        )
        assert scope.get_measurement_period(channel) == approx(1 / frequency, rel=0.1)
        assert scope.get_measurement_average(channel, interval="CYCL") == approx(
            vmax * duty, abs=0.2
        )
        assert scope.get_measurement_base(channel) == approx(0.0, abs=0.2)
        assert scope.get_measurement_max(channel) == approx(vmax, abs=0.2)
        assert scope.get_measurement_min(channel) == approx(0.0, abs=0.2)
        assert scope.get_measurement_peak_to_peak(channel) == approx(vmax, abs=0.5)
        assert scope.get_measurement_voltage_at_time(channel, 1e-6) == approx(
            vmax, abs=0.2
        )
        assert scope.get_measurement_voltage_at_time(channel, 0.5e-3) == approx(
            0.0, abs=0.2
        )
        assert scope.get_measurement_voltage_at_top(channel) == approx(vmax, abs=0.2)

        if measure_counter:
            assert scope.get_measurement_counter(channel) == approx(frequency, rel=0.1)

        if measure_pre_shoot:
            assert scope.get_measurement_pre_shoot(channel) == approx(1, abs=1)

        if extra_measurements:
            assert scope.get_measurement_delay(channel, channel) == 0
            assert scope.get_measurement_fall_time(channel) == approx(0, abs=0.00001)
            time.sleep(0.1)
            assert scope.get_measurement_negative_duty_cycle(channel) == approx(
                nduty, rel=0.1
            )
            assert scope.get_measurement_negative_pulse_width(channel) == approx(
                nduty / frequency, rel=0.1
            )
            assert scope.get_measurement_overshoot(channel) == approx(0, abs=0.1)
            assert scope.get_measurement_phase(channel, channel) == 0
            assert scope.get_measurement_rise_time(channel) == approx(0, abs=0.00001)
            assert scope.get_measurement_transition_time(channel, True, 3) == approx(
                0, abs=0.1
            )
            assert scope.get_measurement_value_time(channel, True, 0.1, 0) == approx(
                0.5e-3, abs=0.1
            )

            # Just to test the command is valid
            scope.set_measurement_window("AUTO")
            scope.set_measurement_edge_spec(1, 4)
            scope.set_measurement_threshold_spec("STANDARD")
            scope.set_measurement_threshold_spec("ABS", 0.9, 0.5, 0.2)
            scope.set_measurement_threshold_spec("PERC", 90, 50, 20)
            scope.set_wavegen_ramp_symmetry(0.5)

        scope.set_wavegen_output_enable(False)

    def test_wavegen(self, scope: OscilloscopeKeysightBase) -> None:
        """Test O10."""
        amplitude = 0.2
        frequency = 1e3
        scope.set_wavegen(
            function="SIN",
            frequency=frequency,
            voltage_high=amplitude / 2.0,
            voltage_low=-amplitude / 2.0,
            output_impedance="ONEM",
        )
        scope.set_wavegen_output_enable(True)

        channel = 2
        scope.set_timebase(timebase_range=10e-3)
        scope.set_channel(
            channel=channel,
            voltage_range=0.5,
            attenuation=1.0,
            offset=0.0,
            coupling="DC",
        )
        scope.set_trigger(
            channel=channel,
            level=0.0,
            slope="POS",
            sweep="NORM",
            coupling="DC",
            mode="EDGE",
        )

        scope.digitize()

        assert scope.get_measurement_frequency(channel) == approx(frequency, rel=0.1)
        assert scope.get_measurement_amplitude(channel) == approx(amplitude, rel=0.2)

        scope.set_wavegen_output_enable(False)
