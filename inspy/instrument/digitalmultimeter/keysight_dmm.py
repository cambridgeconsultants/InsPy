"""Keysight digital multimeter classes."""

from time import sleep
from typing import Literal

from inspy.instrument._base import (
    ErrorCheckedInstrumentMixin,
    VisaInstrumentMixin,
    with_check,
)

from ._base import DigitalMultimeter, DmmError

POLLING_CYCLE = 0.5
Measurements = Literal[
    "VOLT",
    "VOLT:AC",
    "CURR",
    "CURR:AC",
    "RES",
    "FRES",
    "TEMP",
    "FREQ",
    "PER",
    "DIOD",
    "CONT",
    "CAP",
]


class DmmKeysight344xxA(
    ErrorCheckedInstrumentMixin, VisaInstrumentMixin, DigitalMultimeter
):
    """Keysight 344xxA Digital Multimeter Base Class.

    Based on the Keysight 34465A.

    Supports measurement modes: ``VOLT``, ``VOLT:AC``, ``CURR``, ``CURR:AC``, ``RES``,
    ``FRES``, ``TEMP``, ``FREQ``, ``PER``, ``DIOD``, ``CONT``, ``CAP``

    `Keysight 344xxA User Manual <https://www.keysight.com/us/en/assets/7018-03846/data-sheets/5991-1983.pdf>`_
    """  # noqa E501

    _error_class = DmmError

    def reset(self) -> None:
        """Reset instrument to factory default state, including clearing status."""
        self.transport.clear()
        self.transport.command("*CLS")
        self.transport.command("*RST")

    # Measure
    def measure_voltage(self) -> float:
        """Get the measured output DC voltage."""
        return float(self.transport.query("MEAS:VOLT:DC?"))

    def measure_current(self) -> float:
        """Get the measured output DC current."""
        return float(self.transport.query("MEAS:CURR:DC?"))

    def measure_voltage_ac(self) -> float:
        """Get the measured output AC voltage."""
        return float(self.transport.query("MEAS:VOLT:AC?"))

    def measure_current_ac(self) -> float:
        """Get the measured output AC current."""
        return float(self.transport.query("MEAS:CURR:AC?"))

    def measure_resistance(self) -> float:
        """Get the measured resistance."""
        return float(self.transport.query("MEAS:RES?"))

    def measure_resistance_four_wire(self) -> float:
        """Get the measured four wire resistance."""
        return float(self.transport.query("MEAS:FRES?"))

    def measure_temperature(self) -> float:
        """Get the measured temperature."""
        return float(self.transport.query("MEAS:TEMP?"))

    def measure_continuity(self) -> bool:
        """Get continutiy boolean."""
        return bool(self.transport.query("MEAS:CONT?"))

    def measure_diode_bias(self) -> float:
        """Get the forward/reverse bias voltage of the diode."""
        return float(self.transport.query("MEAS:DIOD?"))

    def measure_capacitance(self) -> float:
        """Get the capacitance."""
        return float(self.transport.query("MEAS:CAP?"))

    def measure_frequency(self) -> float:
        """Get the frequency.

        Timeout if frequency is too low. Specify the lowest frequency you expect
        to encounter with `set_frequency_bandwidth()`.
        May take up to 10s for low frequencies.
        """
        original_timeout = self.transport.get_timeout()
        self.transport.set_timeout(timeout=10.0)
        return_val = float(self.transport.query("MEAS:FREQ?"))
        self.transport.set_timeout(timeout=original_timeout)
        return return_val

    def measure_period(self) -> float:
        """Get the period.

        Timeout if period is too high. Specify the lowest frequency you expect
        to encounter with `set_frequency_bandwidth()`.
        May take up to 10s for low frequencies.
        """
        original_timeout = self.transport.get_timeout()
        self.transport.set_timeout(timeout=10.0)
        return_val = float(self.transport.query("MEAS:PER?"))
        self.transport.set_timeout(timeout=original_timeout)
        return return_val

    def set_measure_frequency_bandwidth(self, bandwidth: float) -> None:
        """Set the AC bandwidth for frequency and period measurements.

        The instrument selects the slow (3 Hz), medium (20 Hz) or fast (200 Hz)
        filter based on the cutoff frequency specified. Specify the lowest frequency
        you expect to encounter.
        """
        self.transport.command(f"FREQ:RANG:LOW {bandwidth}")

    def get_measure_frequency_bandwidth(self) -> float:
        """Get the AC filter configuration for frequency and period measurements."""
        return float(self.transport.query("FREQ:RANG:LOW?"))

    # Trace
    @with_check
    def set_sampling_measurement_mode(self, function: str = "VOLT") -> None:
        """Set the function or measurement mode to be sampled.

        Supports measurement modes: ``VOLT``, ``VOLT:AC``, ``CURR``, ``CURR:AC``,
        ``RES``, ``FRES``, ``TEMP``, ``FREQ``, ``PER``, ``DIOD``, ``CONT``, ``CAP``

        Args:
            function: The measurement function to be configured for sampling.

        """
        self.transport.command(f"CONF:{function}")

    def get_sampling_measurement_mode(self) -> str:
        """Get the current function or measurement mode that is set for sampling.

        Returns:
            The current function as a string (e.g. ``VOLT:AC``)

        """
        # CONF? returns in the form: "VOLT +1.00000000E+01,+3.00000000E-06"
        config_query = self.transport.query("CONF?")
        # Extract first word, and remove " character.
        return config_query.split()[0][1:]

    @with_check
    def set_averaging_time_NPLC(self, averaging_time: float = 10) -> None:
        """Set the integration time in number of power line cycles.

        The length of a power line cycle for 50 Hz AC is 20ms, integrating the
        DC signal over an number of powerline cycles >1 helps reject power line
        induced AC noise.

        Only for: 'VOLT', 'CURR', 'RES', 'FRES', 'TEMP'
        Args:
            averaging_time: Integration time in number of cycles.
        """
        trace_function = self.get_sampling_measurement_mode()
        if trace_function in ["VOLT", "CURR", "RES", "FRES", "TEMP"]:
            self.transport.command(f"{trace_function}:NPLC {averaging_time}")
        else:
            raise Exception(
                "NPLC command is only supported by VOLT, CURR, RES, FRES, TEMP"
                " Functions."
            )

    def get_averaging_time_NPLC(self) -> float:
        """Get the integration time in number of power line cycles.

        The length of a power line cycle for 50 Hz AC is 20ms, integrating the
        DC signal over a number of powerline cycles >1 helps reject power line
        induced AC noise.

        Only for: 'VOLT', 'CURR', 'RES', 'FRES', 'TEMP'
        Returns:
            Integration time in number of power line cycles.
        """
        trace_function = self.get_sampling_measurement_mode()
        if trace_function in ["VOLT", "CURR", "RES", "FRES", "TEMP"]:
            return float(self.transport.query(f"{trace_function}:NPLC?"))
        else:
            raise Exception(
                "NPLC command is only supported by VOLT, CURR, RES, FRES, TEMP"
                " Functions."
            )

    @with_check
    def set_averaging_time(self, averaging_time: float = 0.1) -> None:
        """Set the integration time in seconds.

        Only for: 'VOLT', 'CURR', 'RES', 'FRES', 'TEMP'
        Args:
            averaging_time: Integration time in seconds.
        """
        trace_function = self.get_sampling_measurement_mode()
        if trace_function in ["VOLT", "CURR", "RES", "FRES", "TEMP"]:
            self.transport.command("VOLT:APER:ENAB 1")
            self.transport.command(f"VOLT:APER {averaging_time}")
        else:
            raise Exception(
                "NPLC command is only supported by VOLT, CURR, RES, FRES, TEMP"
                " Functions."
            )

    def get_averaging_time(self) -> float:
        """Get the integration time in seconds.

        Returns:
            Integration time in seconds.

        """
        trace_function = self.get_sampling_measurement_mode()
        if trace_function in ["VOLT", "CURR", "RES", "FRES", "TEMP"]:
            return float(self.transport.query(f"{trace_function}:APER?"))
        else:
            raise Exception(
                "NPLC command is only supported by VOLT, CURR, RES, FRES, TEMP"
                " Functions."
            )

    @with_check
    def set_measurement_range(self, measurement_range: float | None) -> None:
        """Set a fixed measurement range.

        Applies to the active trace function from get_sampling_measurement_mode().

        Args:
            measurement_range: Measurement range to set. If measurement_range is not
                provided then the default DMM measurement_range is used.

        """
        self.transport.command(
            f"{self.get_sampling_measurement_mode()}:RANG"
            f" {measurement_range if measurement_range else 'DEF'}"
        )

    def get_measurement_range(self) -> float:
        """Get the fixed measurement range.

        Applies to the active trace function from get_sampling_measurement_mode().

        Returns:
            Measurement range.

        """
        return float(
            self.transport.query(f"{self.get_sampling_measurement_mode()}:RANG?")
        )

    def set_measurement_range_auto(self, enable: bool = True) -> None:
        """Set autoranging for measurements.

        Args:
            enable: on/off boolean.

        """
        self.transport.command(
            f"{self.get_sampling_measurement_mode()}:RANG:AUTO {1 if enable else 0}"
        )

    def get_measurement_range_auto(self) -> bool:
        """Get autorange status.

        Returns:
            Autorange status boolean.

        """
        return bool(
            int(
                self.transport.query(
                    f"{self.get_sampling_measurement_mode()}:RANG:AUTO?"
                )
            )
        )

    # Trigger
    def set_trigger_immediate(self) -> None:
        """Set trigger source to immediate.

        Triggers as soon as `set_wait_for_trigger()` is called.
        """
        self.transport.command("TRIG:SOUR IMM")

    def set_trigger_external(self, pos_edge: bool = True) -> None:
        """Set trigger source to external.

        Triggers on external positive/negative edge.

        Args:
            pos_edge: True for positive edge triggering, False for negative.

        """
        self.transport.command("TRIG:SOUR EXT")
        self.transport.command(f"TRIG:SLOP {'POS' if pos_edge else 'NEG'}")

    def set_trigger_internal_level(
        self, trigger_level: float, pos_edge: bool = True
    ) -> None:
        """Set trigger source to internal.

        Triggers when a DMM measurement exceeds a specified trigger_level.
        Can be configured for positive/negative edge triggering.


        Args:
            trigger_level: Trigger level.
            pos_edge: True for positive edge triggering, False for negative.

        """
        self.transport.command("TRIG:SOUR INT")
        self.transport.command(f"TRIG:LEV {trigger_level}")
        self.transport.command(f"TRIG:SLOP {'POS' if pos_edge else 'NEG'}")

    def set_trigger_bus(self) -> None:
        """Set trigger source to BUS.

        Triggers when a trigger command (`*TRG`/`trigger_now()`) is sent
        over a remote interface.
        """
        self.transport.command("TRIG:SOUR BUS")

    def get_trigger_source(self) -> str:
        """Get trigger source setting.

        Returns:
            Current trigger source.

        """
        return self.transport.query("TRIG:SOUR?")

    def trigger_now(self) -> None:
        """Send trigger (`*TRG`) command.

        Used when the trigger source is set to BUS with
        `set_trigger_bus()`.
        """
        self.transport.command("*TRG")

    @with_check
    def set_trigger_delay(self, trigger_delay: float = 1) -> None:
        """Set trigger delay setting.

        Delay after trigger before measurement(s) start.
        Used to allow input to settle before taking measurements.

        Args:
            trigger_delay: Trigger delay setting in seconds.

        """
        self.transport.command(f"TRIG:DEL {trigger_delay}")

    def get_trigger_delay(self) -> float:
        """Get trigger delay.

        Returns:
            Trigger delay setting.

        """
        return float(self.transport.query("TRIG:DEL?"))

    def set_wait_for_trigger(self) -> None:
        """Set the instrument into a wait-for-trigger state.

        After setting the sample count, source, etc. you must place the meter
        in the "wait-for-trigger" state. A trigger is not accepted from the selected
        trigger source until the instrument is in the "wait-for-trigger" state.
        """
        self.transport.command("INIT")

    # Sample
    @with_check
    def set_sample_points(self, sample_points: int = 5) -> None:
        """Set the number of samples for a 'trace' acquisition.

        Args:
            sample_points: Number of samples.

        """
        self.transport.command(f"SAMP:COUN {sample_points}")

    def get_sample_points(self) -> int:
        """Get the number of samples points setting.

        Returns:
            Sample number setting.

        """
        return int(self.transport.query("SAMP:COUN?"))

    @with_check
    def set_sample_interval(self, sample_interval: float = 1) -> None:
        """Set the sample interval for timed sampling.

        Args:
            sample_interval: Time between samples in seconds.

        """
        self.transport.command("SAMP:SOUR TIM")
        self.transport.command(f"SAMP:TIM {sample_interval}")

    def get_sample_interval(self) -> float:
        """Get the sample interval setting for timed sampling.

        The sampling interval is the time between samples.

        Returns:
            Sample interval setting in seconds.

        """
        return float(self.transport.query("SAMP:TIM?"))

    def set_sample_interval_min(self) -> None:
        """Set the recommended interval for the current measurement configuration."""
        self.transport.command("SAMP:SOUR TIM")
        self.transport.command("SAMP:TIM MIN")

    def get_sample_interval_min(self) -> float:
        """Determine the recommended interval for the current measurement configuration.

        Returns:
            Minimum sample interval for current configuration in seconds.

        """
        return float(self.transport.query("SAMP:TIM? MIN"))

    def get_samples(self, polling_cycle: float = POLLING_CYCLE) -> list[float]:
        """Wait for measurements to complete and returns all measurements.

        Polls the device to get trigger state and measuring status.

        Args:
            polling_cycle: Set polling_cycle in seconds.

        Returns:
            List of samples.

        """
        while self.get_wait_for_trigger_status():
            sleep(polling_cycle)
        while self.get_measuring_status():
            sleep(polling_cycle)

        return [float(num) for num in self.transport.query("FETC?").split(",")]

    def get_measuring_status(self) -> bool:
        """Get the 'Measuring' bit from the Standard Operation Register.

        Indicates if the instrument is currently sampling.

        Returns:
            Bit status boolean.

        """
        return bool(
            (int(self.transport.query("STAT:OPER:COND?")) & 0b10000) >> 4
        )  # Reads 5th bit - Measuring status

    def get_wait_for_trigger_status(self) -> bool:
        """Get the 'Waiting for trigger' bit from the Standard Operation Register.

        Returns:
            Bit status boolean.

        """
        return bool(
            (int(self.transport.query("STAT:OPER:COND?")) & 0b100000) >> 5
        )  # Reads 6th bit - Trigger status


class DmmKeysight34461A(DmmKeysight344xxA):
    """Keysight 34461A Digital Multimeter Class.

    Inherits all methods from the DmmKeysight34465A class, and
    adds none.

    `Keysight 34461A User Manual <https://www.keysight.com/gb/en/assets/9018-03876/service-manuals/9018-03876.pdf>`_
    """  # noqa E501

    pass


class DmmKeysight34465A(DmmKeysight344xxA):
    """Keysight 34465A Digital Multimeter Class.

    Inherits all methods from the DmmKeysight344xxA class, and
    adds none.

    `Keysight 34465A User Manual <https://www.keysight.com/gb/en/assets/9018-03876/service-manuals/9018-03876.pdf>`_
    """  # noqa E501
