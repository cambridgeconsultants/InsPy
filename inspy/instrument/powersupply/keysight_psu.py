"""Keysight Power Supply instrument class."""

from time import sleep

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    VisaInstrumentMixin,
    with_check,
)
from inspy.instrument.powersupply._base import PowerSupply, PowerSupplyError

# Delay required for trip status to be reliably updated after a trip event occurs.
TRIP_STATE_DELAY = 1


class PsuKeysightBase(ErrorCheckedInstrumentMixin, VisaInstrumentMixin, PowerSupply):
    """Base class for Keysight Power Supply instruments."""

    _error_class = PowerSupplyError

    def _append_channel_string(
        self, channel: int, command: str, space: bool = False
    ) -> str:
        """Modify command to handle multiple channels.

        Args:
            channel: Channel number to modify command for.
            command: Command to modify.
            space: Use a space separator instead of the default comma.

        Returns:
            Modified command with channel number.

        """
        if len(self.channels) == 1:
            return command
        else:
            separator = " " if space else ","
            return command + f"{separator}(@{channel})"

    @with_check
    def set_channel_state(self, enable: bool = True, channel: int = 1) -> None:
        """Set channel on or off.

        Args:
            channel: Channel to enable/disable.
            enable: True(on) or False(off).

        """
        assert channel in self.channels, self.channel_error_message

        command = f"OUTP {1 if enable else 0}"
        command_with_channel = self._append_channel_string(channel, command)
        self.transport.command(command_with_channel)

    def get_channel_state(self, channel: int = 1) -> bool:
        """Get channel on/off state.

        Args:
            channel: Channel to get.

        Returns:
            Channel state, True(on) or False(off)

        """
        assert channel in self.channels, self.channel_error_message

        command = "OUTP?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return bool(int(self.transport.query(command_with_channel)))

    @with_check
    def set_voltage(self, voltage: float, channel: int = 1) -> None:
        """Set channel voltage.

        Args:
            voltage: Voltage setting.
            channel: Channel to set voltage on.

        """
        assert channel in self.channels, self.channel_error_message

        command = f"VOLT {voltage}"
        command_with_channel = self._append_channel_string(channel, command)
        self.transport.command(command_with_channel)

    def get_voltage(self, channel: int = 1) -> float:
        """Get channel voltage setting.

        Args:
            channel: Channel to get voltage setting from.

        Returns:
            Channel voltage setting

        """
        assert channel in self.channels, self.channel_error_message

        command = "VOLT?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return float(self.transport.query(command_with_channel))

    @with_check
    def set_current(self, current: float, channel: int = 1) -> None:
        """Set current limit on channel.

        Args:
            current: Current limit setting.
            channel: Channel to set limit on.

        """
        assert channel in self.channels, self.channel_error_message

        command = f"CURR {current}"
        command_with_channel = self._append_channel_string(channel, command)
        self.transport.command(command_with_channel)

    def get_current(self, channel: int = 1) -> float:
        """Get current limit on channel.

        Args:
            channel: Channel to get limit on.

        Returns:
            Current limit on the channel.

        """
        assert channel in self.channels, self.channel_error_message

        command = "CURR?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return float(self.transport.query(command_with_channel))

    def measure_voltage(self, channel: int = 1) -> float:
        """Get the measured output voltage of the power supply on a specific channel.

        Args:
            channel: Channel to measure voltage on.

        Returns:
            Measured voltage.

        """
        assert channel in self.channels, self.channel_error_message

        command = "MEAS:VOLT?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return float(self.transport.query(command_with_channel))

    def measure_current(self, channel: int = 1) -> float:
        """Measure output current on a specific channel.

        Args:
            channel: Channel to measure current on.

        Returns:
            Measured current.

        """
        assert channel in self.channels, self.channel_error_message

        command = "MEAS:CURR?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return float(self.transport.query(command_with_channel))

    @with_check
    def set_output_voltage_trip_point(self, voltage: float, channel: int = 1) -> None:
        """Set the output voltage value at which to trip the power supply.

        Args:
            voltage: Voltage trip point.
            channel: Channel to set.

        """
        assert channel in self.channels, self.channel_error_message

        command = f"VOLT:PROT {voltage}"
        command_with_channel = self._append_channel_string(channel, command)
        self.transport.command(command_with_channel)

    def get_output_voltage_trip_point(self, channel: int = 1) -> float:
        """Get the output voltage value at which to trip the power supply.

        Args:
            channel: Channel to set.

        Returns:
            Output voltage trip point setting.

        """
        assert channel in self.channels, self.channel_error_message

        command = "VOLT:PROT?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return float(self.transport.query(command_with_channel))

    def get_voltage_trip_status(self) -> bool:
        """Indicate whether an overvoltage protection occurred.

        Delays by TRIP_STATE_DELAY to ensure overvoltage status has updated.

        Args:
            channel: Channel to check(might not be used).

        Returns:
            Overvoltage protection occured boolean.

        """
        sleep(TRIP_STATE_DELAY)
        return bool(int(self.transport.query("VOLT:PROT:TRIP?")))

    @with_check
    def reset_voltage_trip_with_disable(self, channel: int = 1) -> None:
        """Clear overvoltage protection event. Disables channel.

        Args:
            channel: Channel to clear.

        """
        assert channel in self.channels, self.channel_error_message

        self.set_channel_state(enable=False, channel=channel)
        command = "VOLT:PROT:CLE"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        self.transport.command(command_with_channel)

    def get_current_trip_status(self) -> bool:
        """Indicate wheter an overcurrent protection event occurred.

        Args:
            channel: Channel to check trip status on.

        Returns:
            Overcurrent protection occured boolean.

        """
        sleep(TRIP_STATE_DELAY)
        return bool(int(self.transport.query("CURR:PROT:TRIP?")))

    @with_check
    def set_current_protection_state(
        self, enable: bool = True, channel: int = 1
    ) -> None:
        """Set current protection on a specific channel.

        Trips the channel after 0.05s in current limit mode.

        Args:
            enable: Enable (True) or disable (False) current protection.
            channel: Channel to set.

        """
        assert channel in self.channels, self.channel_error_message

        self.set_channel_state(enable=False, channel=channel)
        command = f"CURR:PROT:STAT {1 if enable else 0}"
        command_with_channel = self._append_channel_string(channel, command)
        self.transport.command(command_with_channel)

    def get_current_protection_state(self, channel: int = 1) -> bool:
        """Check if current protection is enabled.

        Args:
            channel: Channel to check trip status on.

        Returns:
            Overcurrent protection occured boolean.

        """
        assert channel in self.channels, self.channel_error_message

        command = "CURR:PROT:STAT?"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        return bool(int(self.transport.query(command_with_channel)))

    @with_check
    def reset_current_trip_with_disable(self, channel: int = 1) -> None:
        """Clear overcurrent protection event. Disables channel.

        Args:
            channel: Channel to clear overcurrent protection on.

        """
        assert channel in self.channels, self.channel_error_message

        self.set_channel_state(enable=False, channel=channel)
        command = "CURR:PROT:CLE"
        command_with_channel = self._append_channel_string(channel, command, space=True)
        self.transport.command(command_with_channel)

    def reset(self) -> None:
        """Reset instrument to factory settings.

        Includes clearing status register and protection events.
        """
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")
        for channel in self.channels:
            self.reset_voltage_trip_with_disable(channel)
            self.reset_current_trip_with_disable(channel)


class PsuKeysightE36312A(PsuKeysightBase):
    """Power Supply instrument class for the Keysight E36312A.

    This power supply has 3 channels

    Channels 1,2,3 refer to P6V, P25V, and N25V respectively
    # Voltage trip limits: 6.6V,27.5V,27.5V
    # Current Limits: 5A,1A,1A

    `Keysight E36300 User Manual <https://www.keysight.com/gb/en/assets/9018-04577/programming-guides/9018-04577.pdf>`_
    """  # noqa E501

    channels = [1, 2, 3]
