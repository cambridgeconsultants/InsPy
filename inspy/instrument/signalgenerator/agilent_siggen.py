"""Agilent Signal Generator Instrument Classes."""

from typing import Any

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    VisaInstrumentMixin,
    with_check,
)
from inspy.instrument.signalgenerator._base import SignalGenerator
from inspy.utils import validate_args


class SigGenAgilentBase(
    ErrorCheckedInstrumentMixin, VisaInstrumentMixin, SignalGenerator
):
    """Base class for Agilent signal generators."""

    waveform_type_to_scpi = {
        "SINE": "SIN",
        "SQUARE": "SQU",
        "RAMP": "RAMP",
        "PULSE": "PULS",
        "NOISE": "NOIS",
        "DC": "DC",
        "USER": "USER",
    }

    @with_check
    def set_channel_state(self, enable: bool, channel: int = 1) -> None:
        """Enable or Disable the channel(s) output/input.

        tags: Enable, Disable, On, Off, state, channel, Output, Input, Source, Sink

        Args:
            enable: Enable the channel output
            channel: channel(s) to set the state of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"OUTP {'ON' if enable else 'OFF'}")

    def get_channel_state(self, channel: int = 1) -> bool:
        """Get the current state of the output.

        Args:
            channel: channel to get state of

        Returns:
            True if output enabled

        """
        assert channel in self.channels, self.channel_error_message

        return bool(int(self.transport.query("OUTP?")))

    @with_check
    def set_frequency(self, frequency: float, channel: int = 1) -> None:
        """Set the frequency (in Hz) of the required channel(s).

        Args:
            frequency: Frequency in Hz
            channel: Channel(s) to set frequency of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"FREQ {frequency}")

    def get_frequency(self, channel: int = 1) -> float:
        """Get the set frequency of the desired channel.

        Args:
            channel: channel to get the set frequency from

        Returns:
            Frequency in Hz

        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query("FREQ?"))

    @with_check
    def set_voltage_low(self, voltage: float, channel: int = 1) -> None:
        """Set the low/minimum voltage of the signal.

        `set_voltage_low` and `set_voltage_high` are used together.
        Alternatively, you can use `set_voltage_offset` and `set_voltage_amplitude`
        together.

        Args:
            voltage: Low/minimum voltage of signal
            channel: Channel(s) to set voltage of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"VOLT:LOW {voltage}")

    def get_voltage_low(self, channel: int = 1) -> float:
        """Get the currently set low/minimum voltage of the signal.

        Args:
            channel: Channel to get the set low voltage of

        Returns:
            Voltage in V

        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query("VOLT:LOW?"))

    @with_check
    def set_voltage_high(self, voltage: float, channel: int = 1) -> None:
        """Set the high/maximum voltage of the signal.

        `set_voltage_low` and `set_voltage_high` are used together.
        Alternatively, you can use `set_voltage_offset` and `set_voltage_amplitude`
        together.

        Args:
            voltage: High/maximum voltage of signal
            channel: Channel(s) to set voltage of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"VOLT:HIGH {voltage}")

    def get_voltage_high(self, channel: int = 1) -> float:
        """Get the currently set high/maximum voltage of the signal.

        Args:
            channel: Channel to get the set high voltage of

        Returns:
            Voltage in V

        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query("VOLT:HIGH?"))

    @with_check
    def set_voltage_amplitude(self, voltage: float, channel: int = 1) -> None:
        """Set the amplitude of the signal.

        `set_voltage_offset` and `set_voltage_amplitude` are used together.
        Alternatively, you can use `set_voltage_low` and `set_voltage_high` together.

        Args:
            voltage: Amplitude of the signal in V
            channel: Channel(s) to set voltage of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"VOLT {voltage}")

    def get_voltage_amplitude(self, channel: int = 1) -> float:
        """Get the currently set amplitude of the signal.

        Args:
            channel: Channel to get the set amplitude of

        Returns:
            Voltage in V

        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query("VOLT?"))

    @with_check
    def set_voltage_offset(self, voltage: float, channel: int = 1) -> None:
        """Set the offset of the signal.

        `set_voltage_offset` and `set_voltage_amplitude` are used together.
        Alternatively, you can use `set_voltage_low` and `set_voltage_high` together.

        Args:
            voltage: Offset of the signal in V
            channel: Channel(s) to set voltage of

        """
        assert channel in self.channels, self.channel_error_message

        self.transport.command(f"VOLT:OFFS {voltage}")

    def get_voltage_offset(self, channel: int = 1) -> float:
        """Get the currently set offset of the signal.

        Args:
            channel: Channel to get the set offset of

        Returns:
            Voltage in V

        """
        assert channel in self.channels, self.channel_error_message

        return float(self.transport.query("VOLT:OFFS?"))

    @with_check
    def set_impedance(self, impedance: str, channel: int = 1) -> None:
        """Set the output impedance of the channel.

        Args:
            impedance: string of impedance mode.
                Can be only '50' (50 Ohm) or 'HIGH' (1 Meg typ.)
            channel: Channel to set impedance of

        """
        assert channel in self.channels, self.channel_error_message
        if impedance == "50":
            self.transport.command("OUTP:LOAD 50")
        elif impedance == "HIGH":
            self.transport.command("OUTP:LOAD INF")
        else:
            raise ValueError(
                f"Unknown impedance value: {impedance}\nValid values are '50' or 'HIGH'"
            )

    def get_impedance(self, channel: int = 1) -> str:
        """Get the set impedance of the channel.

        Args:
            channel: Channel to get the set impedance of

        Returns:
            Impedance string ('50', 'HIGH')

        """
        assert channel in self.channels, self.channel_error_message
        impedance = self.transport.query("OUTP:LOAD?")

        # Convert impedance to a float
        impedance_value = round(float(impedance), 1)

        if impedance_value == 50.0:
            return "50"
        elif impedance_value == 9.9e37:
            return "HIGH"
        else:
            raise ValueError(
                f"Unknown impedance value: {impedance}\nExpected values are 50 or"
                " 9.9e37"
            )

    @with_check
    @validate_args(mode=list(waveform_type_to_scpi.keys()))
    def set_waveform_mode(
        self,
        mode: str,
        channel: int = 1,
    ) -> None:
        """Set the type/shape of the waveform.

        For user waveform, you can set the waveform using set_new_arbitrary_waveform()
        or select a waveform from the saved waveforms using set_saved_user_waveform()
        and then set the waveform mode to USER using this function.

        Args:
            mode ('SINE' | 'SQUARE' | 'RAMP' | 'PULSE' | 'NOISE' | 'DC' | 'USER'):
                Type of waveform to set
            channel: channel to set waveform type of

        """
        assert channel in self.channels, self.channel_error_message
        assert mode in self.waveform_type_to_scpi, (
            f"Unknown mode value: {mode}\n"
            f"Valid modes are: {', '.join(self.waveform_type_to_scpi.keys())}"
        )
        self.transport.command(f"FUNC {self.waveform_type_to_scpi[mode]}")

    def get_waveform_mode(self, channel: int = 1) -> str:
        """Get the type/shape of the waveform.

        Args:
            channel: Channel to get the set waveform of

        Returns:
            Waveform type as string

        """
        assert channel in self.channels, self.channel_error_message

        result = self.transport.query("FUNC?")
        assert result in self.scpi_to_waveform_type, (
            f"Unknown mode value: {result}\n"
            f"Valid modes are: {', '.join(self.scpi_to_waveform_type.keys())}"
        )

        return self.scpi_to_waveform_type[result]

    def get_saved_user_waveforms(self, channel: int = 1) -> list[str]:
        """Get the list of saved user waveforms in the signal generator.

        Args:
            channel: Channel to get the user waveforms from

        Returns:
            List of user waveform names

        """
        assert channel in self.channels, self.channel_error_message

        # Returns the names in the form of
        # "TEST1_ARB","TEST2_ARB","TEST3_ARB","TEST4_ARB"
        result = self.transport.query("DATA:NVOL:CAT?")

        if result == '""':
            return []

        user_waveforms = result.strip('"').split('","')
        return user_waveforms

    @with_check
    def delete_saved_user_waveform(self, name: str = "userFunc") -> None:
        """Delete the user waveform from the signal generator.

        Args:
            name: Name of the user waveform to delete

        """
        # Set the waveform to SINE (default) since you cannot delete if it is selected
        if self.get_waveform_mode() == "USER":
            self.await_completion()
            self.set_waveform_mode("SINE")
            self.logger.info("Waveform mode set to SINE to delete the waveform")

        saved_waveforms = self.get_saved_user_waveforms()

        # Check if the waveform exists in the signal generator
        if name.upper() not in saved_waveforms:
            raise ValueError(
                f"Waveform {name} not found in the signal generator\n"
                f"Waveforms saved: {saved_waveforms}"
            )

        self.await_completion()
        self.transport.command(f"DATA:DEL {name}")

    @with_check
    def delete_all_saved_user_waveforms(self, channel: int = 1) -> None:
        """Delete all the saved arbitrary waveforms in the signal generator.

        Args:
            channel: Channel to delete all saved waveforms of

        """
        assert channel in self.channels, self.channel_error_message

        # Set the waveform to SINE (default) since you cannot delete if it is selected
        if self.get_waveform_mode() == "USER":
            self.await_completion()
            self.set_waveform_mode("SINE")
            self.logger.info("Waveform mode set to SINE to delete the waveform")

        self.await_completion()
        self.transport.command("DATA:DEL:ALL")

    @with_check
    def set_saved_user_waveform(self, name: str = "userFunc", channel: int = 1) -> None:
        """Select the user waveform for the USER mode of the signal generator.

        This method just selects the waveform for the USER mode.
        It does not set the waveform mode to USER.

        Args:
            name: Name of the user waveform to select
            channel: Channel to select the user waveform of

        """
        assert channel in self.channels, self.channel_error_message

        # Check if the waveform exists in the signal generator
        if name.upper() not in self.get_saved_user_waveforms(channel=channel):
            raise ValueError(
                f"Waveform {name} not found in the signal generator\n"
                f"Waveforms saved: {self.get_saved_user_waveforms(channel)}"
            )

        self.await_completion()
        # Set the selected waveform as the active USER waveform
        self.transport.command(f"FUNC:USER {name}")

    @with_check
    def set_new_arbitrary_waveform(
        self, array: list[Any], name: str = "userFunc", channel: int = 1
    ) -> None:
        """Save a new arbitrary waveform to the signal generator's memory.

        This method also sets the waveform mode to USER and enables the channel.

        The array should be a list of values that represent the waveform.

        Examples:

        .. code:: python

            >>> [0.3       ,  0.302002  ,  0.304004  ,  0.30600601,  0.30800801,
            >>>  0.31001001,  0.31201201,  0.31401401,  0.31601602,  0.31801802,
            >>>  0.32002002,  0.32202202,  0.32402402,  0.32602603,  0.32802803,
            >>>  0.33003003,  0.33203203,  0.33403403,  0.33603604,  0.33803804]

        This is an example of a summation of square & sawtooth waveform generated.
        This example is generated using numpy and scipy libraries.

        You can have any arbitrary waveform as long as it is a list of values.
        Ideally you would want to have a large number of points to have a smooth wave.

        The values must be a list of:

        - floating point values from -1.0 to +1.0 (Representing the peaks)

        You can have from 1 to 65,536 such points.
        If less than 16,384 points, a 16,384 point waveform is generated.
        If more than 16,384 points, a 65,536-point waveform is generated.

        You can specify the characteristics of the waveform using other functions.
        For example, you can set the frequency, voltage, offset, etc.

        - If you want a wave from -5V to +5V, you can set the amplitude to 10V
          and use the range of -1.0 to +1.0 in the array.
          -1.0 will be scaled to -5V and +1.0 will be scaled to +5V

        Things to keep in mind:

        Args:
            array: data to set the waveform to be
            name: Name of the waveform to store in the SigGen
            channel: Channel to set the waveform data of

        """
        assert channel in self.channels, self.channel_error_message

        slots_available = int(self.transport.query("DATA:NVOL:FREE?"))
        if slots_available == 0:
            raise ValueError(
                "Cannot store waveform in the SigGen due to unavailable space\n"
                "You can delete waveforms using delete_saved_user_waveform() method\n"
                f"Waveforms saved: {self.get_saved_user_waveforms(channel)}"
            )

        if name.upper() in self.get_saved_user_waveforms(channel=channel):
            raise ValueError(
                f"Waveform {name} already exists in the SigGen\n"
                "Please use a different name or delete the existing waveform"
                " using delete_saved_user_waveform() method"
            )

        self.transport.command(f"DATA VOLATILE, {', '.join(str(x) for x in array)}")
        self.await_completion()
        self.transport.command(f"DATA:COPY {name}")
        self.await_completion()
        self.set_saved_user_waveform(channel=channel, name=name)
        self.await_completion()
        self.set_waveform_mode("USER", channel=channel)
        self.await_completion()
        self.set_channel_state(True, channel)

    def await_completion(self) -> None:
        """Wait for the signal generator to complete the current operation."""
        self.transport.query("*OPC?")

    @with_check
    def reset(self) -> None:
        """Reset the signal generator to default settings."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")
        self.delete_all_saved_user_waveforms()


class SigGenAgilent33220A(SigGenAgilentBase):
    """Signal generator instrument class for 33220A.

    tags: AWG, Arb, Arbitrary Waveform Generator, Function Generator, Keysight
    Suports VISA

    `Agilent 33220A User Manual <https://www.keysight.com/gb/en/assets/9018-04437/user-manuals/9018-04437.pdf>`_
    """  # noqa E501

    channels = [1]
