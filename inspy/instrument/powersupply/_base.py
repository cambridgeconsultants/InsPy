"""Base class and type definitions for power supply."""

from __future__ import annotations

from abc import abstractmethod

from inspy.instrument._base import InstrumentBase, InstrumentError


class PowerSupply(InstrumentBase):
    """A class representing a power supply instrument.

    It includes methods to set the voltage and manage the instrument connection,
    either through context management or by manually calling the close method.
    """

    # For validating channel numbers
    channels: list[int] = []
    channel_error_message = f"Valid channel(s): {', '.join([str(i) for i in channels])}"

    @abstractmethod
    def set_channel_state(self, enable: bool = True, channel: int = 1) -> None:
        """Set a specific channel on or off."""
        pass

    @abstractmethod
    def get_channel_state(self, channel: int = 1) -> bool:
        """Get info on whether a channel is on or off."""
        pass

    @abstractmethod
    def set_voltage(self, voltage: float, channel: int = 1) -> None:
        """Set the voltage of the power supply on a specific channel."""
        pass

    @abstractmethod
    def get_voltage(self, channel: int = 1) -> float:
        """Get the voltage you have set on a specific channel of the power supply."""
        pass

    @abstractmethod
    def set_current(self, current: float, channel: int = 1) -> None:
        """Set the current of the power supply on a specific channel."""
        pass

    @abstractmethod
    def get_current(self, channel: int = 1) -> float:
        """Get the current you have set on a specific channel of the power supply."""
        pass

    @abstractmethod
    def measure_voltage(self, channel: int = 1) -> float:
        """Get the measured output voltage on a specific channel of the power supply."""
        pass

    @abstractmethod
    def measure_current(self, channel: int = 1) -> float:
        """Get the measured output current on a specific channel of the power supply."""
        pass

    @abstractmethod
    def await_completion(self) -> None:
        """Wait for the power supply to finish its current operation."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the power supply to default settings."""
        pass


class PowerSupplyError(InstrumentError):
    """Base class for all power supply related errors."""

    pass
