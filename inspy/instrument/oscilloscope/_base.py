"""Generic Instrument Class for Oscilloscopes."""

from abc import abstractmethod

from inspy.instrument._base import InstrumentBase, InstrumentError


class Oscilloscope(InstrumentBase):
    """Base class for oscilloscopes.

    Specific instruments will use this class as a base.
    It will provide the basic functionality for the instruments.
    """

    # For validating channel numbers
    channels: list[int] = []
    channel_error_message = f"Valid channel(s): {', '.join([str(i) for i in channels])}"

    TimebaseReference: list[str] = []
    ChannelCoupling: list[str] = []
    TriggerSweep: list[str] = []
    TriggerSlope: list[str] = []
    TriggerCoupling: list[str] = []
    TriggerMode: list[str] = []

    @abstractmethod
    def set_timebase(self, timebase_range: float, reference: str) -> None:
        """Configure the timebase.

        Args:
            timebase_range: The duration of the captured waveform in seconds
                (not the time per division).
            reference: The position of the trigger in the waveform.

        """
        pass

    @abstractmethod
    def set_timebase_range(self, timebase_range: float) -> None:
        """Configure the timebase range in seconds."""
        pass

    @abstractmethod
    def get_timebase_range(self) -> float:
        """Get the timebase range in seconds."""
        pass

    @abstractmethod
    def set_timebase_reference(self, reference: str) -> None:
        """Configure the position of the trigger in the waveform."""
        pass

    @abstractmethod
    def get_timebase_reference(self) -> str:
        """Get the position of the trigger in the waveform."""
        pass

    @abstractmethod
    def set_channel(
        self,
        channel: int,
        voltage_range: float,
        offset: float,
        coupling: str,
        attenuation: float,
        bw_limit: bool,
        state: bool,
    ) -> None:
        """Configure input channel.

        Args:
            channel: Number of the channel starting at 1
            voltage_range: Total voltage range for the capture
            offset: Voltage range: {offset - range / 2, offset + range / 2}.
            coupling: DC or AC (i.e. with high pass filter).
            attenuation: Attenuation factor.
            bw_limit: Enable the 25 MHz low-pass filter.
            state: Enable or disable capture and display of the channel.

        """
        pass

    @abstractmethod
    def set_channel_range(self, channel: int, voltage_range: float) -> None:
        """Set the total voltage range for the capture."""
        pass

    @abstractmethod
    def get_channel_range(self, channel: int) -> float:
        """Get the total voltage range for the capture."""
        pass

    @abstractmethod
    def set_channel_offset(self, channel: int, offset: float) -> None:
        """Set the voltage offset.

        The voltage range will be: {offset - range / 2, offset + range / 2}
        """
        pass

    @abstractmethod
    def get_channel_offset(self, channel: int) -> float:
        """Get the voltage offset."""
        pass

    @abstractmethod
    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """Set to DC or AC (i.e. with high pass filter) coupling."""
        pass

    @abstractmethod
    def get_channel_coupling(self, channel: int) -> str:
        """Get coupling type."""
        pass

    @abstractmethod
    def set_channel_attenuation(self, channel: int, attenuation: float) -> None:
        """Set the attenuation  of the channel / probe.

        Note that this effectively changes the channel's input voltage range so it's
        recommended that this is set first.
        """
        pass

    @abstractmethod
    def get_channel_attenuation(self, channel: int) -> float:
        """Set the configured attenuation of the channel."""
        pass

    @abstractmethod
    def set_channel_bw_limit(self, channel: int, bw_limit: bool) -> None:
        """Enable the 25 MHz low-pass filter."""
        pass

    @abstractmethod
    def get_channel_bw_limit(self, channel: int) -> bool:
        """Get the state of the 25 MHz low-pass filter."""
        pass

    @abstractmethod
    def set_channel_state(self, channel: int, state: bool) -> None:
        """Enable capture and display of the channel."""
        pass

    @abstractmethod
    def get_channel_state(self, channel: int) -> bool:
        """Get the state of the capture and display for the channel."""
        pass

    @abstractmethod
    def set_trigger(
        self,
        sweep: str,
        channel: int,
        level: float,
        slope: str,
        coupling: str,
        mode: str,
        noise_reject: bool = False,
        hold_off: float | None = None,
    ) -> None:
        """Configure trigger.

        Args:
            sweep: NORMAL: only trigger when condition met, or AUTO: if trigger isn't
                fired regularly then trigger anyway
            channel: Channel to monitor
            level: Voltage threshold of trigger
            slope: Trigger on positive or negative edges (other options available)
            coupling: DC or AC (i.e. with high pass filter).
            noise_reject: Enable the noise reject filter. Defaults to False.
            hold_off: Time in seconds after a trigger before another trigger may fire.
                Defaults to None.
            mode: Current only edge mode is supported.

        """
        pass

    @abstractmethod
    def set_trigger_sweep(self, sweep: str) -> None:
        """Set the sweep mode of the trigger.

        NORMAL: only trigger when condition met
        AUTO: if trigger isn't fired regularly then trigger anyway.
        """
        pass

    @abstractmethod
    def get_trigger_sweep(self) -> str:
        """Get the sweep mode of the trigger.

        NORMAL: only trigger when condition met
        AUTO: if trigger isn't fired regularly then trigger anyway.
        """
        pass

    @abstractmethod
    def set_trigger_mode(self, mode: str) -> None:
        """Set the mode (e.g. edge, glitch, etc)."""
        pass

    @abstractmethod
    def get_trigger_mode(self) -> str:
        """Get the mode (e.g. edge, glitch, etc)."""
        pass

    @abstractmethod
    def get_trigger_coupling(self) -> str:
        """Get trigger input coupling type."""
        pass

    @abstractmethod
    def set_trigger_noise_reject(self, noise_reject: bool) -> None:
        """Enable noise rejection filter."""
        pass

    @abstractmethod
    def get_trigger_noise_reject(self) -> bool:
        """Get state of noise rejection filter."""
        pass

    @abstractmethod
    def set_trigger_hold_off(self, hold_off: float) -> None:
        """Set minimum gap between triggers."""
        pass

    @abstractmethod
    def get_trigger_hold_off(self) -> float:
        """Get configured minimum gap between triggers."""
        pass

    @abstractmethod
    def trigger_now(self) -> None:
        """Force an immediate capture of data irrespective of the trigger."""
        pass

    @abstractmethod
    def single(self) -> None:
        """Capture a single waveform using the trigger."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Start continuous capture of waveforms."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop continuous capture of waveforms."""
        pass

    @abstractmethod
    def digitize(self) -> None:
        """Capture a single waveform using the trigger."""
        pass

    @abstractmethod
    def get_waveform(self, channel: int) -> tuple[list[float], list[float]]:
        """Get the waveform data of a capture.

        First :obj:`~scope.trigger_now` or
        :obj:`~scope.digitize`.

        Args:
            channel: Channel to get the waveform data from

        Returns:
            A tuple with the first element being a list of the time values and the
            second being a list of the voltages

        """
        pass

    @abstractmethod
    def set_setup(self, data: bytes) -> None:
        """Configure the scope using bytes of a .scp file.

        Example - Load from disk:
            >>> from pathlib import Path
            >>> scope.set_setup(Path('setup.scp').read_bytes())
        """
        pass

    @abstractmethod
    def get_setup(self) -> bytes:
        """Get setup from the scope as bytes of a .scp file.

        Example - Save to disk:
            >>> from pathlib import Path
            >>> Path('setup.scp').write_bytes(scope.get_setup())
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset and clear the scope configuration."""
        pass

    @abstractmethod
    def await_completion(self) -> None:
        """Wait for the scope to finish processing commands."""
        pass


class OscilloscopeError(InstrumentError):
    """Base class for errors raised by the oscilloscopes."""

    pass
