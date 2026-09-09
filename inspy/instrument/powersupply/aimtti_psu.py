"""Aim TTi Power Supply.

NOTE: The USB interface to some TTi power supplies doesn't flush correctly on
Linux, instead use the RS-232 or Ethernet interface.

NOTE: The Ethernet interface requires a raw socket using a VISA address like:
TCPIP0::169.254.136.181::9221::SOCKET

Example VISA resource names:

- RS-232: ``ASRL/dev/ttyUSB0``
- USB: ``ASRL/dev/ttyACM0``
- Ethernet: ``TCPIP0::169.254.136.181::9221::SOCKET``

"""

from time import monotonic
from typing import Literal

from pyvisa.errors import VisaIOError

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    VisaInstrumentMixin,
    with_check,
)

from ._base import PowerSupply, PowerSupplyError

_EXECUTION_ERRORS = {
    100: "Range error: The numeric value sent is not allowed.",
    101: "A recall of set up data has been requested, but the store specified contains"
    " corrupted data. This is either a hardware fault or a temporary data corruption,"
    " which can be corrected by writing data to the store again",
    102: "A recall of set up data has been requested, but the store specified does not"
    " contain any data.",
    103: "Attempt to read or write a command on the second output when it is not"
    " available. Typically occurs when reading / writing a command on the second output"
    " when it is not available, or on a two-channel instrument which is set to"
    " parallel mode",
    104: "Command not valid with output on. Ensure output is off before sending"
    " this command.",
    200: "Read Only: An attempt has been made to change the settings of"
    " the instrument from an interface without write priveleges.",
}

_QUERY_ERRORS = {
    1: "Interrupted: Input queue contains more than one END message or a"
    " <PROGRAM MESSAGE TERMINATOR> has been read by the parser.",
    2: "Deadlock: A response is pending and the input queue is full.",
    3: "Unterminated: The supply is addressed to talk when it has no response to send.",
}


class PsuAimTTiBase(ErrorCheckedInstrumentMixin, VisaInstrumentMixin, PowerSupply):
    """Aim TTi Power supply base class.

    Based on Aim TTi CPX400DP power supply
    Should work with other TTi power supplies, but not tested yet.

    """

    _error_class = PowerSupplyError
    reset_timeout = 5.0

    def get_errors(self) -> list[tuple[int, str]]:
        """Get errors from the TTi execution and query error registers.

        The TTi does not implement the SCPI ``:SYSTem:ERRor?`` queue. Instead
        it provides two read and clear registers returning a bare numeric code.

        Keep in mind, `EER?` is a single register, not a queue.
        This will only hold one error code.
        """
        errors = []
        for register, descriptions in (
            ("EER", _EXECUTION_ERRORS),
            ("QER", _QUERY_ERRORS),
        ):
            code = int(self.transport.query(f"{register}?"))
            if code != 0:
                errors.append(
                    (code, descriptions.get(code, f"Unknown {register} error"))
                )

        return errors

    @with_check
    def set_channel_state(self, enable: bool = True, channel: int = 1) -> None:
        """Set a specific channel on or off."""
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"OP{channel} {1 if enable else 0}")

    def get_channel_state(self, channel: int = 1) -> bool:
        """Get info on whether a channel is on or off."""
        assert channel in self.channels, self.channel_error_message

        return bool(int(self.transport.query(f"OP{channel}?")))

    @with_check
    def set_voltage(self, voltage: float, channel: int = 1) -> None:
        """Set the voltage of the power supply."""
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"V{channel} {voltage:.2f}")

    def get_voltage(self, channel: int = 1) -> float:
        """Set the voltage of the power supply."""
        assert channel in self.channels, self.channel_error_message

        # The query returns a string with the format "V1 5.00V"
        # We split the string using partition which results in [V1, ' ', 5.00V]
        # We then take the last element of the partition and convert it to a float
        return float(self.transport.query(f"V{channel}?").partition(" ")[2])

    @with_check
    def set_current(self, current: float, channel: int = 1) -> None:
        """Set the current of the power supply."""
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"I{channel} {current:.2f}")

    def get_current(self, channel: int = 1) -> float:
        """Get the current of the power supply."""
        assert channel in self.channels, self.channel_error_message

        # The query returns a string with the format "I1 5.00A"
        # We split the string using partition which results in [I1, ' ', 5.00A]
        # We then take the last element of the partition and convert it to a float
        return float(self.transport.query(f"I{channel}?").partition(" ")[2])

    def measure_voltage(self, channel: int = 1) -> float:
        """Get the measured output voltage of the power supply on a specific channel."""
        assert channel in self.channels, self.channel_error_message

        # The query returns a string with the format "5.00V"
        # We take a substring of the query result excluding the last 'V' character
        return float(self.transport.query(f"V{channel}O?")[:-1])

    def measure_current(self, channel: int = 1) -> float:
        """Get the measured output current of the power supply on a specific channel."""
        assert channel in self.channels, self.channel_error_message

        # The query returns a string with the format "5.00A"
        # We take a substring of the query result excluding the last 'A' character
        return float(self.transport.query(f"I{channel}O?")[:-1])

    @with_check
    def set_output_voltage_trip_point(self, voltage: float, channel: int = 1) -> None:
        """Set the output voltage value at which to trip the power supply.

        This is for a specific channel.
        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"OVP{channel} {voltage:.2f}")

    def get_output_voltage_trip_point(self, channel: int = 1) -> float:
        """Get the output voltage value for tripping the power supply.

        This is for a specific channel.
        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query(f"OVP{channel}?"))

    @with_check
    def set_output_current_trip_point(self, current: float, channel: int = 1) -> None:
        """Set the output current value at which to trip the power supply.

        This is for a specific channel.
        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"OCP{channel} {current:.2f}")

    def get_output_current_trip_point(self, channel: int = 1) -> float:
        """Get the output current value at which to trip the power supply.

        This is for a specific channel.
        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query(f"OCP{channel}?"))

    def reset(self) -> None:
        """Reset the power supply."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")

        # Poll await_completion until reset done
        deadline = monotonic() + self.reset_timeout
        while True:
            self.transport.clear()
            try:
                self.await_completion()
                return
            except VisaIOError:
                if monotonic() >= deadline:
                    raise


class PsuAimTTIPL303P(PsuAimTTiBase):
    """Power Supply instrument class for the Aim TTi PL303P.

    AimTTiPSUBase was created for this instrument, this class inherits all methods
    It adds checks for single channel and adds two new method (set_current_range, get_current_range)

    This power supply has 1 channel

    `Aim TTi PL Series User Manual <https://resources.aimtti.com/manuals/New_PL+PL-P_Series_Instruction_Manual-Iss15.pdf>`_
    """  # noqa: E501

    channels = [1]

    @with_check
    def set_current_range(
        self, current_range: Literal["Low", "High"], channel: int = 1
    ) -> None:
        """Set the current range of the channel.

        Requires channel to be switched off before changing.

        Args:
            current_range: Low current range or high current range
            channel: Channel to set range of.

        Raises:
            Exception: Changing current range requires channel to be disabled!
            ValueError: Invalid value for range

        """
        assert channel in self.channels, self.channel_error_message
        assert self.get_channel_state(channel) is False, (
            "Changing current range requires channel to be disabled!"
        )

        if current_range == "Low":
            self.transport.command(f"IRANGE{channel} 1")
        elif current_range == "High":
            self.transport.command(f"IRANGE{channel} 2")
        else:
            raise ValueError("Invalid value for current range. Must be 'Low' or 'High'")

    def get_current_range(self, channel: int = 1) -> str:
        """Get the current range of the channel.

        Args:
            channel: Channel to get range of.

        Raises:
            ValueError: Invalid value for current range

        Returns:
            Current range (Low or High)

        """
        assert channel in self.channels, self.channel_error_message

        res = int(self.transport.query(f"IRANGE{channel}?"))
        if res == 1:
            return "Low"
        elif res == 2:
            return "High"
        else:
            raise ValueError(f"Invalid value for current range: {res}")


class PsuAimTTiPL303QMDP(PsuAimTTiBase):
    """Power Supply instrument class for the Aim TTi PL303QMDP.

    This class inherits all methods from AimTTiPSUBase.
    It adds two new mthods (set_current_range, get_current_range)

    This power supply has 2 channels.

    CAUTION!
    The channels have been swapped to match all other standard power supplies:
    Left hand side = Channel 1, Right hand side = Channel 2
    The SCPI programming manual will state CH1 -> Master which is on the right hand side.
    Due to confusion we have resolved this by applying a conversion for this Class.

    `Aim TTi PL Series User Manual <https://resources.aimtti.com/manuals/New_PL+PL-P_Series_Instruction_Manual-Iss15.pdf>`_
    """  # noqa: E501

    channels = [1, 2]
    swap = {1: 2, 2: 1}

    def set_channel_state(self, enable: bool = True, channel: int = 1) -> None:
        """Set a specific channel on or off."""
        super().set_channel_state(enable, self.swap[channel])

    def get_channel_state(self, channel: int = 1) -> bool:
        """Get info on whether a channel is on or off."""
        return super().get_channel_state(self.swap[channel])

    def set_voltage(self, voltage: float, channel: int = 1) -> None:
        """Set the voltage of the power supply."""
        super().set_voltage(voltage, self.swap[channel])

    def get_voltage(self, channel: int = 1) -> float:
        """Set the voltage of the power supply."""
        return super().get_voltage(self.swap[channel])

    def set_current(self, current: float, channel: int = 1) -> None:
        """Set the current of the power supply."""
        super().set_current(current, self.swap[channel])

    def get_current(self, channel: int = 1) -> float:
        """Get the current of the power supply."""
        return super().get_current(self.swap[channel])

    def measure_voltage(self, channel: int = 1) -> float:
        """Get the measured output voltage of the power supply on a specific channel."""
        return super().measure_voltage(self.swap[channel])

    def measure_current(self, channel: int = 1) -> float:
        """Get the measured output current of the power supply on a specific channel."""
        return super().measure_current(self.swap[channel])

    def set_output_voltage_trip_point(self, voltage: float, channel: int = 1) -> None:
        """Set the output voltage value at which to trip the power supply.

        This is for a specific channel.
        """
        super().set_output_voltage_trip_point(voltage, self.swap[channel])

    def get_output_voltage_trip_point(self, channel: int = 1) -> float:
        """Get the output voltage value for tripping the power supply.

        This is for a specific channel.
        """
        return super().get_output_voltage_trip_point(self.swap[channel])

    def set_output_current_trip_point(self, current: float, channel: int = 1) -> None:
        """Set the output current value at which to trip the power supply.

        This is for a specific channel.
        """
        super().set_output_current_trip_point(current, self.swap[channel])

    def get_output_current_trip_point(self, channel: int = 1) -> float:
        """Get the output current value at which to trip the power supply.

        This is for a specific channel.
        """
        return super().get_output_current_trip_point(self.swap[channel])

    @with_check
    def set_current_range(
        self, current_range: Literal["Low", "High"], channel: int = 1
    ) -> None:
        """Set the current range of the channel.

        Requires channel to be switched off before changing.

        Args:
            current_range: Low current range or high current range
            channel: Channel to set range of.

        Raises:
            Exception: Changing current range requires channel to be disabled!
            ValueError: Invalid value for range

        """
        assert channel in self.channels, self.channel_error_message
        assert self.get_channel_state(channel) is False, (
            "Changing current range requires channel to be disabled!"
        )

        channel = self.swap[channel]

        if current_range == "Low":
            self.transport.command(f"IRANGE{channel} 1")
        elif current_range == "High":
            self.transport.command(f"IRANGE{channel} 2")
        else:
            raise ValueError("Invalid value for current range. Must be 'Low' or 'High'")

    def get_current_range(self, channel: int = 1) -> str:
        """Get the current range of the channel.

        Args:
            channel: Channel to get range of.

        Raises:
            ValueError: Invalid value for current range

        Returns:
            Current range (Low or High)

        """
        assert channel in self.channels, self.channel_error_message
        channel = self.swap[channel]

        res = int(self.transport.query(f"IRANGE{channel}?"))
        if res == 1:
            return "Low"
        elif res == 2:
            return "High"
        else:
            raise ValueError(f"Invalid value for current range: {res}")
