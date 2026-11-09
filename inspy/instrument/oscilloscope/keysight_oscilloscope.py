"""Interface for Keysight Oscilloscopes."""

from typing import no_type_check

from pyvisa.errors import VisaIOError

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    VisaInstrumentMixin,
    with_check,
)
from inspy.transport import PyVisaTransport
from inspy.utils import validate_args

from ._base import Oscilloscope, OscilloscopeError


class OscilloscopeKeysightBase(
    ErrorCheckedInstrumentMixin, VisaInstrumentMixin, Oscilloscope
):
    """Base class for Keysight Oscilloscopes.

    Examples:
        Using a hardware trigger:
            >>> scope.reset()
            >>> scope.set_timebase(timebase_range=10e-3)
            >>> scope.set_channel(channel=1, voltage_range=0.5)
            >>> scope.set_trigger(channel=1, level=0.0,
            ...                   slope='POS',
            ...                   sweep='NORM')
            >>> scope.digitize()
            >>> print(scope.get_measurement_amplitude(channel=1))
            >>> scope.get_waveform(channel=1)
            >>> scope.get_screenshot()

        Using a software trigger:
            >>> scope.reset()
            >>> scope.set_timebase(timebase_range=10e-3)
            >>> scope.set_channel(channel=1, voltage_range=0.5)
            >>> scope.set_trigger(channel=1, level=0.0,
            ...                   slope='POS',
            ...                   sweep='NORM')
            >>> scope.trigger_now()
            >>> print(scope.get_measurement_amplitude(channel=1))
            >>> scope.get_waveform(channel=1)
            >>> scope.get_screenshot()

    """

    TimebaseReference = ["LEFT", "CENT", "RIGH"]
    ChannelCoupling = ["AC", "DC"]
    TriggerSweep = ["NORM", "AUTO"]
    TriggerSlope = ["POS", "NEG", "EITH", "ALT"]
    TriggerCoupling = ["AC", "DC", "LFR"]
    TriggerMode = ["EDGE", "GLIT", "PATT", "SHOL", "TRAN", "TV", "SBUS1"]
    MeasurementInterval = ["CYCL", "DISP"]
    MeasurementAverageType = ["AC", "DC"]
    MeasurementWindow = ["MAIN", "ZOOM", "AUTO"]
    MeasurementThresholdType = ["STANDARD", "PERC", "ABS"]
    WavegenFunction = ["SIN", "SQU", "RAMP", "PULS", "NOIS", "DC"]
    WavegenImpedance = ["ONEM", "FIFT"]

    _error_class = OscilloscopeError

    @validate_args(reference=TimebaseReference)
    def set_timebase(
        self,
        timebase_range: float,
        reference: str = "CENT",
    ) -> None:
        """Configure the timebase.

        Args:
            timebase_range: The duration of the captured waveform in seconds
                (not the time per division).
            reference ('LEFT' | 'CENT' | 'RIGH'):
                The position of the trigger in the waveform.

        """
        self.set_timebase_range(timebase_range)
        self.set_timebase_reference(reference)

    @with_check
    def set_timebase_range(self, timebase_range: float) -> None:
        """Configure the timebase range in seconds."""
        self.transport.command(f":TIMebase:RANGe {timebase_range}")

    def get_timebase_range(self) -> float:
        """Get the timebase range in seconds."""
        return float(self.transport.query(":TIMebase:RANGe?"))

    @with_check
    @validate_args(reference=TimebaseReference)
    def set_timebase_reference(self, reference: str = "CENT") -> None:
        """Configure the position of the trigger in the waveform.

        Args:
            reference ('LEFT' | 'CENT' | 'RIGH'):
                The position of the trigger in the waveform.

        """
        self.transport.command(f":TIMebase:REFerence {reference}")

    def get_timebase_reference(self) -> str:
        """Get the position of the trigger in the waveform."""
        val = self.transport.query(":TIMebase:REFerence?")
        if val in self.TimebaseReference:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':TIMebase:REFerence?' -> '{val}'\n"
                f"Valid timebase reference: {', '.join(self.TimebaseReference)}"
            )

    @validate_args(coupling=ChannelCoupling)
    def set_channel(
        self,
        channel: int,
        voltage_range: float,
        offset: float = 0.0,
        coupling: str = "DC",
        attenuation: float = 10.0,
        bw_limit: bool = False,
        state: bool = True,
    ) -> None:
        """Configure input channel.

        Args:
            channel: Number of the channel starting at 1
            voltage_range: Total voltage range for the capture
            offset: Voltage range: {offset - range / 2, offset + range / 2}.
            coupling ('AC' | 'DC'): Coupling type.
            attenuation: Default of 10.0 for 10x scope probes, set to 1.0 otherwise
            bw_limit: Enable the 25 MHz low-pass filter.
            state: Enable or disable capture and display of the channel.

        """
        # Must set attenuation before range otherwise the scope compensates for the
        # change
        self.set_channel_coupling(channel, coupling)
        self.set_channel_attenuation(channel, attenuation)
        self.set_channel_bw_limit(channel, bw_limit)
        self.set_channel_range(channel, voltage_range)
        self.set_channel_offset(channel, offset)
        self.set_channel_state(channel, state)

    @with_check
    def set_channel_range(self, channel: int, voltage_range: float) -> None:
        """Set the total voltage range for the capture."""
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:RANGe {voltage_range}")

    def get_channel_range(self, channel: int) -> float:
        """Get the total voltage range for the capture."""
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":CHANnel{channel}:RANGe?"))

    @with_check
    def set_channel_offset(self, channel: int, offset: float) -> None:
        """Set the voltage offset.

        The voltage range will be: {offset - range / 2, offset + range / 2}
        """
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:OFFSet {offset}")

    def get_channel_offset(self, channel: int) -> float:
        """Get the voltage offset."""
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":CHANnel{channel}:OFFSet?"))

    @with_check
    @validate_args(coupling=ChannelCoupling)
    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """Set the channel coupling.

        Args:
            channel: Channel number
            coupling ('AC' | 'DC'): Coupling type.

        """
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:COUPling {coupling}")

    def get_channel_coupling(self, channel: int) -> str:
        """Get coupling type."""
        assert channel in self.channels, self.channel_error_message
        val = self.transport.query(f":CHANnel{channel}:COUPling?")
        if val in self.ChannelCoupling:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':CHANnel{channel}:COUPling?' -> '{val}'\n"
                f"Valid channel coupling: {', '.join(self.ChannelCoupling)}"
            )

    @with_check
    def set_channel_attenuation(self, channel: int, attenuation: float) -> None:
        """Set the attenuation  of the channel / probe.

        Note that this effectively changes the channel's input voltage range so it's
        recommended that this is set first.

        The probe attenuation factor may be 0.1 to 1000.
        """
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:PROBe {attenuation}")

    def get_channel_attenuation(self, channel: int) -> float:
        """Set the configured attenuation of the channel."""
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":CHANnel{channel}:PROBe?"))

    @with_check
    def set_channel_bw_limit(self, channel: int, bw_limit: bool = True) -> None:
        """Enable the 25 MHz low-pass filter."""
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:BWLimit {int(bw_limit)}")

    def get_channel_bw_limit(self, channel: int) -> bool:
        """Get the state of the 25 MHz low-pass filter."""
        assert channel in self.channels, self.channel_error_message
        return bool(int(self.transport.query(f":CHANnel{channel}:BWLimit?")))

    @with_check
    def set_channel_state(self, channel: int, state: bool = True) -> None:
        """Enable capture and display of the channel."""
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":CHANnel{channel}:DISPlay {int(state)}")

    def get_channel_state(self, channel: int) -> bool:
        """Get the state of the capture and display for the channel."""
        assert channel in self.channels, self.channel_error_message
        return bool(int(self.transport.query(f":CHANnel{channel}:DISPlay?")))

    @validate_args(
        sweep=TriggerSweep,
        slope=TriggerSlope,
        coupling=TriggerCoupling,
        mode=TriggerMode,
    )
    def set_trigger(
        self,
        sweep: str,
        channel: int,
        level: float,
        slope: str,
        coupling: str = "DC",
        mode: str = "EDGE",
        noise_reject: bool = False,
        hold_off: float | None = None,
    ) -> None:
        """Configure trigger.

        Args:
            sweep ('NORM' | 'AUTO'): NORM: only trigger when condition met, or AUTO:
                if trigger isn't fired regularly then trigger anyway
            channel: Channel to monitor
            level: Voltage threshold of trigger
            slope ('POS' | 'NEG' | 'EITH' | 'ALT'): Positive, negative, etc edge
            coupling ('AC' | 'DC' | 'LFR'): Coupling type.
            noise_reject: Enable the noise reject filter.
            hold_off: Time in seconds after a trigger before another trigger may fire.
            mode ('EDGE' | 'GLIT' | 'PATT' | 'SHOL' | 'TRAN' | 'TV' | 'SBUS1'):
                Currently only 'EDGE' is supported.

        Raises:
            NotImplementedError: If mode is not 'EDGE'

        """
        assert channel in self.channels, self.channel_error_message

        self.set_trigger_sweep(sweep)
        self.set_trigger_mode(mode)
        if mode == "EDGE":
            self.set_trigger_edge_source(channel)
            self.set_trigger_edge_level(level)
            self.set_trigger_edge_slope(slope)
            self.set_trigger_edge_coupling(coupling)
        else:
            raise NotImplementedError(
                "set_trigger currently only supports configuring edge mode triggers."
            )
        self.set_trigger_noise_reject(noise_reject)
        if hold_off is not None:
            self.set_trigger_hold_off(hold_off)

    @with_check
    @validate_args(sweep=TriggerSweep)
    def set_trigger_sweep(self, sweep: str) -> None:
        """Set the sweep mode of the trigger.

        NORM: only trigger when condition met
        AUTO: if trigger isn't fired regularly then trigger anyway.

        Args:
            sweep ('NORM' | 'AUTO'): Sweep mode.

        """
        self.transport.command(f":TRIGger:SWEep {sweep}")

    def get_trigger_sweep(self) -> str:
        """Get the sweep mode of the trigger.

        NORMAL: only trigger when condition met
        AUTO: if trigger isn't fired regularly then trigger anyway.
        """
        val = self.transport.query(":TRIGger:SWEep?")
        if val in self.TriggerSweep:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':TRIGger:SWEep?' -> '{val}'\n"
                f"Valid trigger sweep: {', '.join(self.TriggerSweep)}"
            )

    @validate_args(mode="TriggerMode")
    def set_trigger_mode(self, mode: str) -> None:
        """Set the trigger mode.

        Args:
            mode ('EDGE' | 'GLIT' | 'PATT' | 'SHOL' | 'TRAN' | 'TV' | 'SBUS1'): Mode.

        """
        self.transport.command(f":TRIGger:MODE {mode}")

    def get_trigger_mode(self) -> str:
        """Get the mode (e.g. edge, glitch, etc)."""
        val = self.transport.query(":TRIGger:MODE?")
        if val in self.TriggerMode:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':TRIGger:MODE?' -> '{val}'\n"
                f"Valid trigger mode: {', '.join(self.TriggerMode)}"
            )

    @with_check
    def set_trigger_edge_source(self, channel: int) -> None:
        """Set the channel monitored."""
        assert channel in self.channels, self.channel_error_message
        self.transport.command(f":TRIGger:EDGE:SOURce CHANnel{channel}")

    def get_trigger_edge_source(self) -> int:
        """Get the channel monitored."""
        return int(self.transport.query(":TRIGger:EDGE:SOURce?").partition("CHAN")[2])

    @with_check
    def set_trigger_edge_level(self, level: float) -> None:
        """Set the voltage threshold of trigger."""
        self.transport.command(f":TRIGger:EDGE:LEVel {level}")

    def get_trigger_edge_level(self) -> float:
        """Get the voltage threshold of trigger."""
        return float(self.transport.query(":TRIGger:EDGE:LEVel?"))

    @with_check
    @validate_args(slope=TriggerSlope)
    def set_trigger_edge_slope(self, slope: str) -> None:
        """Set positive, negative, etc edge sensitive.

        NOTE: Not valid in TV mode.

        Args:
            slope ('POS' | 'NEG' | 'EITH' | 'ALT'): Positive, negative, etc edge.

        """
        self.transport.command(f":TRIGger:EDGE:SLOPe {slope}")

    def get_trigger_slope(self) -> str:
        """Get edge sensitivity type.

        Not valid in TV mode.
        """
        val = self.transport.query(":TRIGger:EDGE:SLOPe?")
        if val in self.TriggerSlope:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':TRIGger:EDGE:SLOPe?' -> '{val}'\n"
                f"Valid trigger slope: {', '.join(self.TriggerSlope)}"
            )

    @with_check
    @validate_args(coupling=TriggerCoupling)
    def set_trigger_edge_coupling(self, coupling: str) -> None:
        """Set trigger input coupling type.

        Args:
            coupling ('AC' | 'DC' | 'LFR'): Coupling type.

        """
        self.transport.command(f":TRIGger:EDGE:COUPling {coupling}")

    def get_trigger_coupling(self) -> str:
        """Get trigger input coupling type."""
        val = self.transport.query(":TRIGger:EDGE:COUPling?")
        if val in self.TriggerCoupling:
            return val
        else:
            raise ValueError(
                f"Unexpected response to ':TRIGger:EDGE:COUPling?' -> '{val}'\n"
                f"Valid trigger coupling: {', '.join(self.TriggerCoupling)}"
            )

    @with_check
    def set_trigger_noise_reject(self, noise_reject: bool = True) -> None:
        """Enable noise rejection filter."""
        self.transport.command(f":TRIGger:NREJect {int(noise_reject)}")

    def get_trigger_noise_reject(self) -> bool:
        """Get state of noise rejection filter."""
        return bool(int(self.transport.query(":TRIGger:NREJect?")))

    @with_check
    def set_trigger_hold_off(self, hold_off: float) -> None:
        """Set minimum gap between triggers.

        Range is 6e-8 s to 10 s.
        """
        self.transport.command(f":TRIGger:HOLDoff {hold_off}")

    def get_trigger_hold_off(self) -> float:
        """Get configured minimum gap between triggers."""
        return float(self.transport.query(":TRIGger:HOLDoff?"))

    @with_check
    def trigger_now(self) -> None:
        """Force an immediate capture of data irrespective of the trigger."""
        # A delay between the :TRIGger:FORCe and :DIGitize commands appears to break
        # this. Not sure if there's a better way
        self.transport.command(":SINGLE\r\n:TRIGger:FORCe\r\n:DIGitize")

    @with_check
    def single(self) -> None:
        """Capture a single waveform using the trigger."""
        self.transport.command(":SINGLE")

    @with_check
    def run(self) -> None:
        """Start continuous capture of waveforms."""
        self.transport.command(":RUN")

    @with_check
    def stop(self) -> None:
        """Stop continuous capture of waveforms."""
        self.transport.command(":STOP")

    @with_check
    def digitize(self) -> None:
        """Capture a single waveform using the trigger.

        Raises:
            VisaIOError: If timeout (`self.transport.resource.timeout`) expired
            whilst waiting for trigger

        """
        self.transport.command(":DIGitize")

    def get_waveform(self, channel: int) -> tuple[list[float], list[float]]:
        """Get the waveform data of a capture.

        First scope.trigger_now() or scope.digitize().

        Args:
            channel: Channel to get the waveform data from

        Returns:
            A tuple with the first element being a list of the time values and the
            second being a list of the voltages

        """
        assert channel in self.channels, self.channel_error_message

        if not isinstance(self.transport, PyVisaTransport):
            raise NotImplementedError(
                "This function is only supported when using PyVisaTransport."
            )

        self.transport.command(f":WAVeform:SOURce CHANnel{channel}")
        self.transport.command(":WAVeform:FORMat WORD")
        self.transport.command(":WAVeform:BYTeorder LSBFirst")
        self.transport.command(":WAVeform:UNSigned 0")

        (
            format_st,
            type_st,  # noqa: F84
            points_st,
            count_st,  # noqa: F84
            x_increment_st,
            x_origin_st,
            x_reference_st,  # noqa: F84
            y_increment_st,
            y_origin_st,
            y_reference_st,  # noqa: F84
        ) = self.transport.query(":WAVeform:PREamble?").split(",")
        assert int(format_st) == 1  # Word format
        points = int(points_st)
        x_increment = float(x_increment_st)
        x_origin = float(x_origin_st)
        y_increment = float(y_increment_st)
        y_origin = float(y_origin_st)

        xs = [x_origin + n * x_increment for n in range(points)]

        ys_int = self.transport.query_for_block_data(":WAVeform:DATA?", "h", list)
        ys = [y_origin + v * y_increment for v in ys_int]
        return xs, ys

    @with_check
    def set_setup(self, data: bytes) -> None:
        """Configure the scope using bytes of a .scp file.

        Example - Load from disk:
            >>> from pathlib import Path
            >>> scope.set_setup(Path('setup.scp').read_bytes())
        """
        if isinstance(self.transport, PyVisaTransport):
            self.transport.command_with_block_data(":SYSTem:SETup", data)
        else:
            self.logger.error("This function is only supported for PyVisaTransport.")

    def get_setup(self) -> bytes:
        """Get setup from the scope as bytes of a .scp file.

        Example - Save to disk:
            >>> from pathlib import Path
            >>> Path('setup.scp').write_bytes(scope.get_setup())
        """
        if not isinstance(self.transport, PyVisaTransport):
            raise NotImplementedError(
                "This function is only supported when using PyVisaTransport."
            )

        return self.transport.query_for_block_data(":SYSTem:SETup?")

    def get_screenshot(self) -> bytes:
        """Get screenshot from the scope as PNG format bytes.

        Example - Save to disk:
            >>> from pathlib import Path
            >>> Path('screenshot.png').write_bytes(scope.get_screenshot())

        Example - Open with PIL and then save as a JPEG:
            >>> import PIL.Image
            >>> from io import BytesIO
            >>> im = PIL.Image.open(BytesIO(scope.get_screenshot()))
            >>> im.save('screenshot.jpg')

        Example - View in Jupyter notebook
            >>> from IPython.display import Image
            >>> Image(scope.get_screenshot())
        """
        if not isinstance(self.transport, PyVisaTransport):
            raise NotImplementedError(
                "This function is only supported when using PyVisaTransport."
            )
        self.transport.command(":HARDcopy:INKSaver OFF")
        return self.transport.query_for_block_data(":DISPlay:DATA? PNG, COLor")

    @with_check
    def set_measurement_delay(self, channel_a: int, channel_b: int) -> None:
        """Display the measurement the delay time in seconds between two channels.

        See also: :obj:`~scope.set_measurement_edge_spec`

        Args:
            channel_a: Channel number
            channel_b: Channel number

        Returns:
            Delay time in seconds.

        """
        assert channel_a in self.channels, self.channel_error_message
        assert channel_b in self.channels, self.channel_error_message
        self.transport.command(f":MEASure:DELay CHANnel{channel_a},CHANnel{channel_b}")

    def get_measurement_counter(self, channel: int) -> float:
        """Measure the counter frequency in Hertz.

        Args:
            channel: Channel number

        Returns:
            Counter frequency in Hertz.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:COUNter? CHANnel{channel}"))

    def get_measurement_delay(self, channel_a: int, channel_b: int) -> float:
        """Measure the delay time in seconds between two channels.

        See also: :obj:`~scope.set_measurement_edge_spec`

        Args:
            channel_a: Channel number
            channel_b: Channel number

        Returns:
            Delay time in seconds.

        """
        assert channel_a in self.channels, self.channel_error_message
        assert channel_b in self.channels, self.channel_error_message
        return float(
            self.transport.query(
                f":MEASure:DELay? CHANnel{channel_a},CHANnel{channel_b}"
            )
        )

    def get_measurement_duty_cycle(self, channel: int) -> float:
        """Measure the ratio of positive pulse width to period.

        Args:
            channel: Channel number

        Returns:
            Ratio of positive pulse width to period.

        """
        assert channel in self.channels, self.channel_error_message
        # Its divided by 100 because duty cycle = (+pulse width/period)*100
        return (
            float(self.transport.query(f":MEASure:DUTYcycle? CHANnel{channel}")) / 100
        )

    def get_measurement_fall_time(self, channel: int) -> float:
        """Measure the time in seconds between the lower and upper thresholds.

        Args:
            channel: Channel number

        Returns:
            Time in seconds between the lower and upper thresholds.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:FALLtime? CHANnel{channel}"))

    def get_measurement_frequency(self, channel: int) -> float:
        """Measure the frequency in Hertz.

        Args:
            channel: Channel number

        Returns:
            Frequency in Hertz.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:FREQuency? CHANnel{channel}"))

    def get_measurement_negative_duty_cycle(self, channel: int) -> float:
        """Measure the ratio of negative pulse width to period.

        Args:
            channel: Channel number

        Returns:
            Ratio of negative pulse width to period.

        """
        assert channel in self.channels, self.channel_error_message

        try:
            result = self.transport.query(f":MEASure:NDUTy? CHANnel{channel}")
        except VisaIOError:
            try:
                # To clear the error.
                # Apparently there are two errors that need to be cleared
                _ = self.transport.query("SYST:ERR?")
                _ = self.transport.query("SYST:ERR?")
                result = self.transport.query(f":MEASure:NDUTYcycle? CHANnel{channel}")
            except VisaIOError as exc:
                raise ValueError(
                    "This function is not supported for this instrument."
                ) from exc

        return float(result) / 100

    def get_measurement_negative_pulse_width(self, channel: int) -> float:
        """Measure the negative pulse width in seconds.

        Args:
            channel: Channel number

        Returns:
            Negative pulse width in seconds.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:NWIDth? CHANnel{channel}"))

    def get_measurement_overshoot(self, channel: int) -> float:
        """Measure the the ratio of the overshoot of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            The ratio of the overshoot of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return (
            float(self.transport.query(f":MEASure:OVERshoot? CHANnel{channel}")) / 100.0
        )

    def get_measurement_period(self, channel: int) -> float:
        """Measure the waveform period in seconds.

        Args:
            channel: Channel number

        Returns:
            Waveform period in seconds.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:PERiod? CHANnel{channel}"))

    def get_measurement_phase(self, channel_a: int, channel_b: int) -> float:
        """Measure the the phase angle value in degrees between two channels.

        Args:
            channel_a: Channel number
            channel_b: Channel number

        Returns:
            The phase angle value in degrees.

        """
        assert channel_a in self.channels, self.channel_error_message
        assert channel_b in self.channels, self.channel_error_message
        return float(
            self.transport.query(
                f":MEASure:PHASe? CHANnel{channel_a},CHANnel{channel_b}"
            )
        )

    def get_measurement_pre_shoot(self, channel: int) -> float:
        """Measure the the percent of pre-shoot of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            The percent of pre-shoot of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:PREShoot? CHANnel{channel}"))

    def get_measurement_positive_pulse_width(self, channel: int) -> float:
        """Measure the width of positive pulse in seconds.

        Args:
            channel: Channel number

        Returns:
            Width of positive pulse in seconds.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:PWIDth? CHANnel{channel}"))

    def get_measurement_rise_time(self, channel: int) -> float:
        """Measure the rise time in seconds.

        Args:
            channel: Channel number

        Returns:
            Rise time in seconds.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:RISetime? CHANnel{channel}"))

    def get_measurement_transition_time(
        self, channel: int, positive: bool, occurrence: int
    ) -> float:
        """Measure the time in seconds of the specified transition.

        Args:
            channel: Channel number
            positive: Positive (True) or negative (False) edge
            occurrence: Which edge to measure the time to

        Returns:
            Time in seconds of the specified transition.

        """
        assert channel in self.channels, self.channel_error_message
        return float(
            self.transport.query(
                ":MEASure:TEDGe?"
                f" {'+' if positive else '-'}{occurrence},CHANnel{channel}"
            )
        )

    def get_measurement_value_time(
        self, channel: int, positive: bool, value: float, occurrence: int
    ) -> float:
        """Measure the time in seconds of the specified value crossing.

        Args:
            channel: Channel number
            positive: Positive (True) or negative (False) edge
            value: Voltage level whose crossing is measured
            occurrence: Which edge to measure the time to

        Returns:
            Time in seconds of the specified value crossing.

        """
        assert channel in self.channels, self.channel_error_message
        return float(
            self.transport.query(
                ":MEASure:TVALue?"
                f" {value},{'+' if positive else '-'}{occurrence},CHANnel{channel}"
            )
        )

    def get_measurement_amplitude(self, channel: int) -> float:
        """Measure the the amplitude of the selected waveform in volts.

        Args:
            channel: Channel number

        Returns:
            The amplitude of the selected waveform in volts.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VAMPlitude? CHANnel{channel}"))

    def get_measurement_average(self, channel: int, interval: str) -> float:
        """Measure the calculated average voltage.

        Args:
            channel: Channel number
            interval: The interval / window to measure the average over

        Returns:
            Calculated average voltage.

        """
        assert channel in self.channels, self.channel_error_message
        assert interval in self.MeasurementInterval, (
            f"Valid measurement interval: {', '.join(self.MeasurementInterval)}"
        )

        return float(
            self.transport.query(f":MEASure:VAVerage? {interval},CHANnel{channel}")
        )

    def get_measurement_base(self, channel: int) -> float:
        """Measure the value at the base of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            Value at the base of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VBASe? CHANnel{channel}"))

    def get_measurement_max(self, channel: int) -> float:
        """Measure the maximum voltage of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            Maximum voltage of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VMAX? CHANnel{channel}"))

    def get_measurement_min(self, channel: int) -> float:
        """Measure the minimum voltage of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            Minimum voltage of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VMIN? CHANnel{channel}"))

    def get_measurement_peak_to_peak(self, channel: int) -> float:
        """Measure the voltage peak-to-peak of the selected waveform.

        Args:
            channel: Channel number

        Returns:
            Voltage peak-to-peak of the selected waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VPP? CHANnel{channel}"))

    @validate_args(interval=MeasurementInterval, avg_type=MeasurementAverageType)
    def get_measurement_rms(self, channel: int, interval: str, avg_type: str) -> float:
        """Measure the calculated RMS voltage.

        Args:
            channel: Channel number
            interval ('CYCL' | 'DISP'):
                The interval / window to measure the average over
            avg_type ('AC' | 'DC'): The type of average to calculate

        Returns:
            Calculated RMS voltage.

        """
        assert channel in self.channels, self.channel_error_message
        return float(
            self.transport.query(
                f":MEASure:VRMS? {interval},{avg_type},CHANnel{channel}"
            )
        )

    def get_measurement_voltage_at_time(self, channel: int, time: float) -> float:
        """Measure the voltage at the specified time.

        Args:
            channel: Channel number
            time: Time offset in seconds

        Returns:
            Voltage at the specified time.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VTIMe? {time},CHANnel{channel}"))

    def get_measurement_voltage_at_top(self, channel: int) -> float:
        """Measure the voltage at the top of the waveform.

        Args:
            channel: Channel number

        Returns:
            Voltage at the top of the waveform.

        """
        assert channel in self.channels, self.channel_error_message
        return float(self.transport.query(f":MEASure:VTOP? CHANnel{channel}"))

    @with_check
    @validate_args(window_type=MeasurementWindow)
    def set_measurement_window(self, window_type: str) -> None:
        """Use the zoomed window or the full time base for measurement functions.

        Args:
            window_type ('MAIN' | 'ZOOM' | 'AUTO'): The window type.

        """
        self.transport.command(f":MEASure:WINDow {window_type}")

    @with_check
    def set_measurement_edge_spec(self, edge_1: int, edge_2: int) -> None:
        """Set specify the edge numbers used for measuring the delay between.

        See:
            :obj:`~scope.get_measurement_delay`

        Args:
            edge_1: The edge number to start measuring the delay from
            edge_2: The edge number to stop measuring the delay at

        """
        self.transport.command(f":MEASure:DEFine DELay,{edge_1},{edge_2}")

    @with_check
    @validate_args(threshold_type=MeasurementThresholdType)
    def set_measurement_threshold_spec(
        self,
        threshold_type: str,
        upper: float | None = None,
        middle: float | None = None,
        lower: float | None = None,
    ) -> None:
        """Configure the thresholds used by many measurement functions.

        Note that the standard and percentage thresholds are relative to the histogram
        derived range of the waveform.

        Note:
        The standard type uses 90%, 50%, 10% as the upper, middle, lower thresholds
        The percentage type uses the percentage of the histogram derived range (0-100)
        The absolute type uses the absolute voltage value (can be floating point)

        Args:
            threshold_type ('STANDARD' | 'PERC' | 'ABS'): The type of threshold to set
            upper: Lower threshold as percentage or absolute value depending on type
            middle: Lower threshold as percentage or absolute value depending on type
            lower: Lower threshold as percentage or absolute value depending on type

        """
        if threshold_type == "STANDARD":
            return self.transport.command(
                f":MEASure:DEFine THResholds,{threshold_type}"
            )
        else:
            assert all(x is not None for x in [upper, middle, lower]), (
                "All thresholds must be set"
            )
            return self.transport.command(
                ":MEASure:DEFine"
                f" THResholds,{threshold_type},{upper:f},{middle:f},{lower:f}"
            )

    @validate_args(function=WavegenFunction, output_impedance=WavegenImpedance)
    def set_wavegen(
        self,
        function: str,
        frequency: float,
        voltage_high: float,
        voltage_low: float,
        output_impedance: str,
        output_inverted: bool = False,
        pulse_width: float | None = None,
        ramp_symmetry: float | None = None,
        duty_cycle: float | None = None,
    ) -> None:
        """Configure the waveform generator.

        This function aims to configure all of the required settings for the waveform
        generator, with the exception of the output_enable. It first resets the waveform
        generator so that the configuration is always consistent and then applies all of
        the settings. Afterwards set_wavegen_output_enable should be called to actually
        enable the output.

        Example simple sine wave output:
            >>> scope.set_wavegen(
            ...     function='SIN',
            ...     frequency=1e3,
            ...     voltage_high=0.1,
            ...     voltage_low=-0.1,
            ...     output_impedance='ONEM',
            ... )
            >>> scope.set_wavegen_output_enable(True)

        Args:
            function ('SIN' | 'SQU' | 'RAMP' | 'PULS' | 'NOIS' | 'DC'):
                Shape of the wave
            frequency: Frequency in Hz
            voltage_high: Maximum voltage of the waveform
            voltage_low: Minimum voltage of the waveform
            output_impedance ('ONEM' | 'FIFT'): High-impedance or 50R mode
            output_inverted: True or False.
            pulse_width: Width of the pulse for PULSE functions in seconds.
            ramp_symmetry: Time ratio (0.0-1.0) of negative slope to positive slope.
            duty_cycle: Time ratio (0.0-1.0) of high verse total period.

        Raises:
            TypeError: If pulse_width is not set when function is PULSE
            TypeError: If pulse_width is set when function is not PULSE
            TypeError: If ramp_symmetry is not set when function is RAMP
            TypeError: If ramp_symmetry is set when function is not RAMP
            TypeError: If duty_cycle is not set when function is SQUARE
            TypeError: If duty_cycle is set when function is not SQUARE

        """
        self.transport.command(":WGEN:RST")

        self.set_wavegen_function(function)
        self.set_wavegen_frequency(frequency)
        # Set the output load before the voltage: the allowed amplitude/offset
        # range depends on the load (roughly 2x larger into high-Z than into
        # 50R), so the voltage must be validated against the requested load.
        self.set_wavegen_output_impedance(output_impedance)
        self.set_wavegen_voltage(voltage_low, voltage_high)

        if function == "PULS":
            if pulse_width is None:
                raise TypeError("pulse_width required when function == PULSE")
            self.set_wavegen_pulse_width(pulse_width)
        elif pulse_width is not None:
            raise TypeError("pulse_width should not be set when function != PULSE")

        if function == "RAMP":
            if ramp_symmetry is None:
                raise TypeError("ramp_symmetry required when function == RAMP")
            self.set_wavegen_ramp_symmetry(ramp_symmetry)
        elif ramp_symmetry is not None:
            raise TypeError("ramp_symmetry should not be set when function != RAMP")

        if function == "SQU":
            if duty_cycle is None:
                raise TypeError("duty_cycle required when function == SQUARE")
            self.set_wavegen_duty_cycle(duty_cycle)
        elif duty_cycle is not None:
            raise TypeError("duty_cycle should not be set when function != SQUARE")

        self.set_wavegen_output_inverted(output_inverted)

    @with_check
    def set_wavegen_output_enable(self, enable: bool) -> None:
        """Enable the wavegen output."""
        self.transport.command(f":WGEN:OUTPut {int(enable)}")

    @with_check
    @validate_args(function=WavegenFunction)
    def set_wavegen_function(self, function: str) -> None:
        """Set the wavegen function.

        Args:
            function ('SIN' | 'SQU' | 'RAMP' | 'PULS' | 'NOIS' | 'DC'):
                Shape of the wave

        """
        self.transport.command(f":WGEN:FUNCtion {function}")

    @with_check
    def set_wavegen_frequency(self, frequency: float) -> None:
        """Set the wavegen frequency."""
        self.transport.command(f":WGEN:FREQuency {frequency}")

    @with_check
    def set_wavegen_voltage(self, voltage_low: float, voltage_high: float) -> None:
        """Set the wavegen voltage range.

        Warning:
                Output may glitch through a 0 V offset.

        Sets amplitude and offset rather than :VOLTage:HIGH / :VOLTage:LOW.
        :HIGH and :LOW must stay at least the minimum amplitude apart and each
        command is validated against the *current* value of the other, so
        stepping between two valid ranges one endpoint at a time can transiently
        cross over and be rejected with -222 Data out of range (e.g. raising
        :LOW above the present :HIGH, or lowering :HIGH below the present :LOW).
        Amplitude and offset have no such mutual constraint.

        Setting :VOLTage or :VOLTage:OFFSet individually is still validated
        against the other's current value (the output must stay within the
        generator's window), so going directly from one valid state to another
        can pass through an out-of-range intermediate. Zeroing the offset first
        avoids this from any starting state: offset 0 is in range for any valid
        amplitude, the new amplitude is in range at offset 0, and the target
        offset is in range for the new amplitude.
        """
        amplitude = voltage_high - voltage_low
        offset = (voltage_high + voltage_low) / 2.0
        self.transport.command(":WGEN:VOLTage:OFFSet 0")
        self.transport.command(f":WGEN:VOLTage {amplitude}")
        self.transport.command(f":WGEN:VOLTage:OFFSet {offset}")

    @with_check
    def set_wavegen_pulse_width(self, pulse_width: float) -> None:
        """Set the pulse width where applicable."""
        self.transport.command(f":WGEN:FUNCtion:PULSe:WIDTh {pulse_width}")

    @with_check
    def set_wavegen_ramp_symmetry(self, ramp_symmetry: float) -> None:
        """Set the ramp symmetry.

        Time ratio (0.0-1.0) of negative slope to positive slope.

        Example values:
            >>> 0.0: Sawtooth with negative gradient ramps
            >>> 0.5: Triangle wave
            >>> 1.0: Sawtooth with positive gradient ramps

        Args:
            ramp_symmetry: Symmetry of the ramp waveform

        """
        self.transport.command(f":WGEN:FUNCtion:RAMP:SYMMetry {ramp_symmetry * 100}")

    @with_check
    def set_wavegen_duty_cycle(self, duty_cycle: float) -> None:
        """Set the duty cycle.

        Time ratio (0.0-1.0) of high verse total period
        """
        self.transport.command(f":WGEN:FUNCtion:SQUARE:DCYCle {duty_cycle * 100}")

    @with_check
    @validate_args(output_impedance=WavegenImpedance)
    def set_wavegen_output_impedance(self, output_impedance: str) -> None:
        """Set high-impedance or 50R mode.

        Args:
            output_impedance ('ONEM' | 'FIFT'): High-impedance or 50R mode

        """
        self.transport.command(f":WGEN:OUTPut:LOAD {output_impedance}")

    @with_check
    def set_wavegen_output_inverted(self, output_inverted: bool) -> None:
        """Invert the voltage waveform."""
        inverted_st = "INV" if output_inverted else "NORM"
        self.transport.command(f":WGEN:OUTPut:POLarity {inverted_st}")

    @with_check
    def reset(self) -> None:
        """Reset and clear the scope configuration."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")
        self.transport.command(":BLANK")
        self.transport.command(":STOP")
        self.transport.command(":DISPlay:CLEar")


class OscilloscopeKeysight1000XSeriesBase(OscilloscopeKeysightBase):
    """Oscilloscope instrument class for the Keysight 1000X series."""

    @with_check
    def reset(self) -> None:
        """Reset and clear the scope configuration."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")
        self.transport.command(":BLANK")
        self.transport.command(":STOP")
        self.transport.command(":DISPlay:CLEar")


# Concrete implementation
class OscilloscopeKeysightDSOX1102G(OscilloscopeKeysight1000XSeriesBase):
    """Oscilloscope instrument class for the Keysight DSO-X 1102G.

    It inherits all the methods from base class and adds one,
    (get_measurement_bit_rate).

    Reference:
    https://www.keysight.com/zz/en/assets/9018-07554/programming-guides/9018-07554.pdf
    """

    channels = [1, 2]


class OscilloscopeKeysight1200XSeriesBase(OscilloscopeKeysightBase):
    """Oscilloscope instrument class for the Keysight 1200X series."""

    TriggerMode = [
        "EDGE",
        "GLIT",
        "PATT",
        "SHOL",
        "TRAN",
        "TV",
        "SBUS1",
    ]


# Concrete implementation
class OscilloscopeKeysightDSOX1202G(OscilloscopeKeysight1200XSeriesBase):
    """Oscilloscope instrument class for the Keysight DSOX1202G.

    It inherits all the methods from base class and adds none.

    Reference:
    https://www.keysight.com/gb/en/assets/9018-07747/programming-guides/9018-07747.pdf
    """

    channels = [1, 2]


# Concrete implementation


# Concrete implementation


class OscilloscopeKeysight2000XSeriesBase(OscilloscopeKeysightBase):
    """Oscilloscope instrument class for the Keysight 2000X series."""

    TriggerMode = [
        "EDGE",
        "GLIT",
        "PATT",
        "TV",
        "DEL",
        "EBUR",
        "OR",
        "RUNT",
        "SHOL",
        "TRAN",
        "SBUS1",
        "USB",
    ]

    @with_check
    def set_channel_attenuation(self, channel: int, attenuation: float) -> None:
        """Set the attenuation  of the channel / probe.

        Note that this effectively changes the channel's input voltage range so it's
        recommended that this is set first.

        The probe attenuation factor may be 0.001 to 1000.
        """
        super().set_channel_attenuation(channel, attenuation)

    @validate_args(mode=TriggerMode)
    def set_trigger_mode(self, mode: str) -> None:
        """Set the trigger mode.

        Args:
            mode ('EDGE' | 'GLIT' | 'PATT' | 'TV' | 'DEL' | 'EBUR' | 'OR' | 'RUNT' | 'SHOL' | 'TRAN' | 'SBUS1' | 'USB'): The trigger mode

        """  # noqa: E501
        super().set_trigger_mode(mode)

    @with_check
    def set_trigger_hold_off(self, hold_off: float) -> None:
        """Set minimum gap between triggers.

        Range is 4e-8 ns to 10 s.
        """
        super().set_trigger_hold_off(hold_off)

    @no_type_check
    def get_measurement_counter(self, channel: int) -> float:
        """Not applicable for this instrument."""
        self.logger.error(
            "This instrument does not support the measurement counter function"
        )

    def set_wavegen_output_inverted(self, output_inverted: bool) -> None:
        """Not applicable for this instrument."""
        self.logger.error(
            "This instrument does not support the wavegen output inverted function"
        )


# Concrete implementation


# Concrete implementation


# Concrete implementation
class OscilloscopeKeysightDSOX2024A(OscilloscopeKeysight2000XSeriesBase):
    """Oscilloscope instrument class for the Keysight DSOX2024A.

    It inherits all the methods from base class and adds none.

    Reference:
    https://www.keysight.com/gb/en/assets/9018-06893/programming-guides/9018-06893.pdf
    """

    channels = [1, 2, 3, 4]


# Concrete implementation


# Concrete implementation


# Concrete implementation


# Concrete implementation


# Concrete implementation
