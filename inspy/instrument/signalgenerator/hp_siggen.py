"""HP Signal Generator Instrument Classes."""

from typing import Any, no_type_check

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    SerialInstrumentMixin,
    with_check,
)
from inspy.instrument.signalgenerator._base import SignalGenerator
from inspy.transport.serial_transport import SerialTransport
from inspy.utils import validate_args


class SigGenHPBase(ErrorCheckedInstrumentMixin, SerialInstrumentMixin, SignalGenerator):
    """Base class for HP signal generators."""

    waveform_type_to_scpi = {
        "SINE": "SIN",
        "SQUARE": "SQU",
        "TRIANGLE": "TRI",
        "RAMP": "RAMP",
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

    def set_voltage_low(self, voltage: float, channel: int = 1) -> None:
        """Not applicable for this instrument."""
        self.logger.error("This instrument does not support setting the low voltage.")

    @no_type_check
    def get_voltage_low(self, channel: int = 1) -> float:
        """Not applicable for this instrument."""
        self.logger.error("This instrument does not support getting the low voltage.")

    def set_voltage_high(self, voltage: float, channel: int = 1) -> None:
        """Not applicable for this instrument."""
        self.logger.error("This instrument does not support setting the high voltage.")

    @no_type_check
    def get_voltage_high(self, channel: int = 1) -> float:
        """Not applicable for this instrument."""
        self.logger.error("This instrument does not support getting the high voltage.")

    @with_check
    def set_voltage_amplitude(self, voltage: float, channel: int = 1) -> None:
        """Set the amplitude of the signal.

        `set_voltage_offset` and `set_voltage_amplitude` are used together.

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
            impedance: string of impedance mode
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

        For arb waveform, you can set the waveform using set_new_arbitrary_waveform()
        or select a waveform from the saved waveforms using set_saved_user_waveform()
        and then set the waveform mode to USER using this function.

        Args:
            mode ('SINE' | 'SQUARE' | 'TRIANGLE' | 'RAMP' | 'NOISE' | 'DC' | 'USER'):
                Type of waveform to set
            channel: channel to set waveform type of

        """  # noqa: E501
        assert channel in self.channels, self.channel_error_message
        assert mode in self.waveform_type_to_scpi, (
            f"Unknown mode value: {mode}\n"
            f"Valid modes are: {', '.join(self.waveform_type_to_scpi.keys())}"
        )
        self.transport.command(f"FUNC:SHAP {self.waveform_type_to_scpi[mode]}")

    def get_waveform_mode(self, channel: int = 1) -> str:
        """Get the type/shape of the waveform.

        Args:
            channel: Channel to get the set waveform of

        Returns:
            Waveform type as string

        """
        assert channel in self.channels, self.channel_error_message

        result = self.transport.query("FUNC:SHAP?")
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
        for channel in self.channels:
            if self.get_waveform_mode(channel) == "USER":
                self.set_saved_user_waveform("SINC", channel)
                self.set_waveform_mode("DC", channel)
                self.logger.info("Waveform mode set to DC to delete the waveform")

        self.transport.command(f"DATA:DEL {name}")

    @with_check
    def delete_all_saved_user_waveforms(self, channel: int = 1) -> None:
        """Delete all the saved arbitrary waveforms in the signal generator.

        Args:
            channel: Channel to delete all saved waveforms of

        """
        assert channel in self.channels, self.channel_error_message

        # Waveforms are shared between channels need to make sure none are using it
        for channel in self.channels:
            if self.get_waveform_mode() == "USER":
                self.set_saved_user_waveform("SINC", channel)
                self.set_waveform_mode("DC", channel)
                self.logger.info("Waveform mode set to DC to delete the waveform")

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
        self.transport.command(f"FUNC:USER {name}")

    @with_check
    def set_new_arbitrary_waveform(
        self, array: list[Any], name: str = "userFunc", channel: int = 1
    ) -> None:
        """Save a new arbitrary waveform to the signal generator's memory.

        This method also sets the waveform mode to USER and enables the channel.

        The array should be a list of values that represent the waveform.

        Examples:
            >>> [0.3       ,  0.302002  ,  0.304004  ,  0.30600601,  0.30800801,
            >>>  0.31001001,  0.31201201,  0.31401401,  0.31601602,  0.31801802,
            >>>  0.32002002,  0.32202202,  0.32402402,  0.32602603,  0.32802803,
            >>>  0.33003003,  0.33203203,  0.33403403,  0.33603604,  0.33803804]

        This is an example of a summation of square & sawtooth waveform generated.
        This example is generated using numpy and scipy libraries.

        You can have any arbitrary waveform as long as it is a list of values.
        Ideally you would want to have a large number of points to have a smooth wave.

        The values must be a list of:
            >>> floating point values from -1.0 to +1.0 (Representing the peaks)

        You can specify the characteristics of the waveform using other functions.
        For example, you can set the frequency, amplitude, offset, etc.

        To be noted:
            >>> If you want a wave from -5V to +5V, you can set the amplitude to 10V
            ... and use the range of -1.0 to +1.0 in the array.
            ... -1.0 will be scaled to -5V and +1.0 will be scaled to +5V

        Things to keep in mind:
            >>> The sig gen will distribute the array evenly in time over the period
            ... (= 1 / set frequency) specified, and linearly interpolate between them
            >>> It is up to the user to ensure the number of points in the waveform is
            ... high enough to accurately represent the equivalent analogue signal
            ... (>> 2* the key max frequency of interest, as per Nyquist sampling)
            >>> The sample rate indicates the digitisation frequency of the instrument,
            ... and if your signal frequencies approach this value you may not get the
            ... instrument accurately reproducing the signal as it cannot sample fast
            ... enough. In that case, the user should get a different instrument
            ... that supports higher sampling frequencies

        Args:
            array: data to set the waveform to be
            name: Name of the waveform to save
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

        self.transport.command(f"DATA VOLATILE, {','.join(str(x) for x in array)}")
        self.await_completion()
        self.transport.command(f"DATA:COPY {name}")
        self.await_completion()
        self.set_saved_user_waveform(channel=channel, name=name)
        self.await_completion()
        self.set_waveform_mode("USER", channel=channel)
        self.await_completion()
        self.set_channel_state(True, channel)

    @with_check
    def reset(self) -> None:
        """Reset the signal generator to default settings."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")


class SigGenHP33120A(SigGenHPBase):
    """Signal generator instrument class for 33120A.

    tags: AWG, Arb, Arbitrary Waveform Generator, Function Generator, Keysight
    Suports VISA

    Instructions:
    https://www.keysight.com/gb/en/assets/9018-04436/user-manuals/9018-04436.pdf
    """

    channels = [1]

    def __init__(
        self,
        visa_address: str | None = None,
        transport: SerialTransport | None = None,
    ) -> None:
        """Build a serial transport from a VISA resource name."""
        if transport is None and visa_address is not None:
            transport = SerialTransport(
                visa_resource_name=visa_address,
                baudrate=9600,
                dtr=True,
                dsrdtr=True,
                timeout=30.0,
            )
        super().__init__(transport=transport)

    def set_channel_state(self, enable: bool, channel: int = 1) -> None:
        """The 33120A output is always on and cannot be switched off.

        Args:
            enable: Requested output state (only ``True`` is achievable).
            channel: Channel to set the state of.

        """
        assert channel in self.channels, self.channel_error_message
        if not enable:
            self.logger.error(
                "The HP 33120A output cannot be disabled; it is always on. "
                "To produce zero output, set a 0 V DC waveform instead."
            )

    def get_channel_state(self, channel: int = 1) -> bool:
        """Return the output state, which is always enabled on the 33120A.

        The 33120A output cannot be switched off (there is no ``OUTPut[:STATe]``
        command), so this always reports ``True``.

        Args:
            channel: Channel to get the state of.

        Returns:
            Always ``True``.

        """
        assert channel in self.channels, self.channel_error_message
        return True

    def reset(self) -> None:
        """Reset to defaults and clear all stored user (arbitrary) waveforms.

        In addition to the standard ``*RST``, this empties the non-volatile ARB
        memory so the instrument starts from a known, empty state (the 33120A has
        only four non-volatile ARB slots, and a full memory blocks new waveforms).

        Warning:
            This permanently deletes any user waveforms stored on the instrument.

        """
        super().reset()
        self.delete_all_saved_user_waveforms()
