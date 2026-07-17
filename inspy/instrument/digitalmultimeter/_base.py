"""Base class and type definitions."""

from __future__ import annotations

from abc import abstractmethod

from inspy.instrument._base import InstrumentBase, InstrumentError


class DigitalMultimeter(InstrumentBase):
    """A class representing a digital multimeter instrument.

    Provides methods for single measurements, sampling, and managing the
    instrument connection. The connection can be managed through context
    management or by manually calling the `disconnect()` method.
    """

    # Measure
    @abstractmethod
    def measure_voltage(self) -> float:
        """Get the measured output DC voltage."""
        pass

    @abstractmethod
    def measure_voltage_ac(self) -> float:
        """Get the measured output AC voltage."""
        pass

    @abstractmethod
    def measure_current(self) -> float:
        """Get the measured output DC current."""
        pass

    @abstractmethod
    def measure_current_ac(self) -> float:
        """Get the measured output AC current."""
        pass

    @abstractmethod
    def measure_resistance(self) -> float:
        """Get the measured resistance."""
        pass

    @abstractmethod
    def measure_continuity(self) -> bool:
        """Get continutiy.

        Returns a boolean indicating the presence of a complete path
        for current flow.
        """
        pass

    @abstractmethod
    def set_sampling_measurement_mode(self, function: str) -> None:
        """Set the function or measurement mode to be sampled.

        Args:
            function: The measurement function to be configured for sampling.

        """
        pass

    @abstractmethod
    def get_sampling_measurement_mode(self) -> str:
        """Get the current function or measurement mode that is set for sampling.

        Returns:
            The current function as a string (e.g. ``VOLT:AC``)

        """
        pass

    @abstractmethod
    def set_averaging_time(self, averaging_time: float = 0.1) -> None:
        """Set the integration time in seconds."""
        pass

    @abstractmethod
    def get_averaging_time(self) -> float:
        """Get the integration time in seconds."""
        pass

    # Trigger
    @abstractmethod
    def set_trigger_immediate(self) -> None:
        """Set trigger source to immediate.

        Triggers as soon as `set_wait_for_trigger()` is called.
        """
        pass

    @abstractmethod
    def set_wait_for_trigger(self) -> None:
        """Set the instrument into a wait-for-trigger state.

        After setting the sample count, source, etc. you must place the meter
        in the "wait-for-trigger" state. A trigger is not accepted from the selected
        trigger source until the instrument is in the "wait-for-trigger" state.
        """
        pass

    # Sample
    @abstractmethod
    def set_sample_points(self, sample_points: int) -> None:
        """Set the number of samples for a 'trace' acquisition.

        Args:
            sample_points: Number of samples.

        """
        pass

    @abstractmethod
    def get_sample_points(self) -> int:
        """Get the number of samples points setting.

        Returns:
            Sample number setting.

        """
        pass

    @abstractmethod
    def set_sample_interval(self, sample_interval: float) -> None:
        """Set the sample interval for timed sampling.

        Args:
            sample_interval: Time between samples in seconds.

        """
        pass

    @abstractmethod
    def get_sample_interval(self) -> float:
        """Get the sample interval setting for timed sampling.

        The sampling interval is the time between samples.

        Returns:
            Sample interval setting in seconds.

        """
        pass

    @abstractmethod
    def get_samples(self) -> list[float]:
        """Wait for measurements to complete and returns all measurements."""
        pass


class DmmError(InstrumentError):
    """Base class for errors raised by the Digital Multimeter."""

    pass
