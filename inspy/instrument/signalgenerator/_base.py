"""Generic Instrument Class for Signal generators.

(Signal, Waveform, Function including Arbitrary)
"""

from abc import abstractmethod
from typing import Any

from inspy.instrument import InstrumentBase


class SignalGenerator(InstrumentBase):
    """Base Signal generator class.

    This implements (Arbitrary) Signal, Waveform, Function Generators.
    Specific instruments will use this class as a base.
    It will provide the basic functionality for the instruments.
    """

    # For validating channel numbers
    channels: list[int] = []
    channel_error_message = f"Valid channel(s): {', '.join([str(i) for i in channels])}"

    # Maps the type of waveform to generate to SCPI command syntax to send to the
    # SigGen.
    waveform_type_to_scpi: dict[str, str] = {}

    @property
    def scpi_to_waveform_type(self) -> dict[str, str]:
        """Map the SCPI query result from the SigGen to type of waveform.

        Done to update the attribute when the waveform_type_to_scpi is redefined.
        Otherwise, the scpi_to_waveform_type will not be updated and will always be {}.
        """
        return {v: k for k, v in self.waveform_type_to_scpi.items()}

    @abstractmethod
    def set_channel_state(self, enable: bool, channel: int = 1) -> None:
        """Enable or Disable the channel(s) output/input.

        tags: Enable, Disable, On, Off, state, channel, Output, Input, Source, Sink

        Args:
            enable: Enable the channel output?
            channel: channel(s) to set the state of

        """
        pass

    @abstractmethod
    def get_channel_state(self, channel: int = 1) -> bool:
        """Get the current state of the output.

        Args:
            channel: channel to get state of

        Returns:
            True if output enabled

        """
        pass

    @abstractmethod
    def set_frequency(self, frequency: float, channel: int = 1) -> None:
        """Set the frequency (in Hz) of the required channel(s).

        Args:
            frequency: Frequency in Hz
            channel: Channel(s) to set frequency of

        """
        pass

    @abstractmethod
    def get_frequency(self, channel: int = 1) -> float:
        """Get the set frequency of the desired channel.

        Args:
            channel: channel to get the set frequency from

        Returns:
            Frequency in Hz

        """
        pass

    @abstractmethod
    def set_voltage_low(self, voltage: float, channel: int = 1) -> None:
        """Set the low/minimum voltage of the signal.

        `set_voltage_low` and `set_voltage_high` are used together.
        Alternatively, you can use `set_voltage_offset` and `set_voltage_amplitude`
        together.

        Args:
            voltage: Low/minimum voltage of signal
            channel: Channel(s) to set voltage of

        """
        pass

    @abstractmethod
    def get_voltage_low(self, channel: int = 1) -> float:
        """Get the currently set low/minimum voltage of the signal.

        Args:
            channel: Channel to get the set low voltage of

        Returns:
            Voltage in V

        """
        pass

    @abstractmethod
    def set_voltage_high(self, voltage: float, channel: int = 1) -> None:
        """Set the high/maximum voltage of the signal.

        `set_voltage_low` and `set_voltage_high` are used together.
        Alternatively, you can use `set_voltage_offset` and `set_voltage_amplitude`
        together.

        Args:
            voltage: High/maximum voltage of signal
            channel: Channel(s) to set voltage of

        """
        pass

    @abstractmethod
    def get_voltage_high(self, channel: int = 1) -> float:
        """Get the currently set high/maximum voltage of the signal.

        Args:
            channel: Channel to get the set high voltage of

        Returns:
            Voltage in V

        """
        pass

    @abstractmethod
    def set_voltage_amplitude(self, voltage: float, channel: int = 1) -> None:
        """Set the amplitude of the signal.

        `set_voltage_offset` and `set_voltage_amplitude` are used together.
        Alternatively, you can use `set_voltage_low` and `set_voltage_high` together.

        Args:
            voltage: Amplitude of the signal in V
            channel: Channel(s) to set voltage of

        """
        pass

    @abstractmethod
    def get_voltage_amplitude(self, channel: int = 1) -> float:
        """Get the currently set amplitude of the signal.

        Args:
            channel: Channel to get the set amplitude of

        Returns:
            Voltage in V

        """
        pass

    @abstractmethod
    def set_voltage_offset(self, voltage: float, channel: int = 1) -> None:
        """Set the offset of the signal.

        `set_voltage_offset` and `set_voltage_amplitude` are used together.
        Alternatively, you can use `set_voltage_low` and `set_voltage_high` together.

        Args:
            voltage: Offset of the signal in V
            channel: Channel(s) to set voltage of

        """
        pass

    @abstractmethod
    def get_voltage_offset(self, channel: int = 1) -> float:
        """Get the currently set offset of the signal.

        Args:
            channel: Channel to get the set offset of

        Returns:
            Voltage in V

        """
        pass

    @abstractmethod
    def set_impedance(self, impedance: str, channel: int = 1) -> None:
        """Set the output impedance of the channel.

        Args:
            impedance: string of impedance mode
                (Concrete implementations will define valid values for impedance)
            channel: Channel to set impedance of

        """
        pass

    @abstractmethod
    def get_impedance(self, channel: int = 1) -> str:
        """Get the set impedance of the channel.

        Args:
            channel: Channel to get the set impedance of

        Returns:
            Impedance mode as string

        """
        pass

    @abstractmethod
    def set_waveform_mode(self, mode: str, channel: int = 1) -> None:
        """Set the type/shape of the waveform.

        Valid waveform modes are:
            'MODE1', 'MODE2', 'MODE3', 'MODE4' (Change in each instrument)

        Args:
            mode: Type of waveform to set
            channel: channel to set waveform type of

        """
        pass

    @abstractmethod
    def get_waveform_mode(self, channel: int = 1) -> str:
        """Get the type/shape of the waveform.

        Args:
            channel: Channel to get the set waveform of

        Returns:
            Waveform type as string

        """
        pass

    @abstractmethod
    def set_new_arbitrary_waveform(
        self, array: list[Any], name: str = "userFunc", channel: int = 1
    ) -> None:
        """Save a new arbitrary waveform to the signal generator's memory.

        This method also sets the waveform mode to USER and enables the channel.

        Args:
            array: data to set the waveform to be
            name: Name of the waveform to save
            channel: Channel to set the waveform data of

        """
        pass

    @abstractmethod
    def await_completion(self) -> None:
        """Wait for all pending operations to complete."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the signal generator to default settings."""
        pass
