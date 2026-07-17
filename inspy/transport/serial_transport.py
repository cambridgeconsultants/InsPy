"""Serial transport layer for communication with devices."""

import time

from pyvisa.rname import ASRLInstr, ResourceName, USBInstr, USBRaw
from serial import PortNotOpenError, Serial, SerialException
from serial.tools import list_ports

from inspy.utils import validate_args

from ._base import TransportBase


class SerialTransport(TransportBase):
    """Transport layer for using serial communication."""

    @validate_args(parity=["N", "E", "O", "S", "M"])
    def __init__(
        self,
        visa_resource_name: str | None = None,
        port: str | None = None,
        vid: int | None = None,
        pid: int | None = None,
        serial_number: str | None = None,
        baudrate: int = 115200,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: int = 1,
        timeout: float = 2.0,
        command_delay: float = 0.0,
        dtr: bool | None = None,
        rts: bool | None = None,
        dsrdtr: bool = False,
        rtscts: bool = False,
        xonxoff: bool = False,
    ) -> None:
        """Initialize SerialTransport with serial port settings.

        Either the port can be specified, or the USB VID and PID. Optionally if the USB
        VID and PID are provided then the serial_number can also be specified.

        Args:
            visa_resource_name: https://pyvisa.readthedocs.io/en/latest/introduction/names.html#visa-resource-syntax-and-examples
            port: COM port name.
            vid: USB vendor ID.
            pid: USB product ID.
            serial_number: USB serial number.
            baudrate: Communication speed in bits per second.
            bytesize: Number of data bits.
            parity ('N' | 'E' | 'O' | 'S' | 'M'): Parity setting.
            stopbits: Number of stop bits.
            timeout: Read timeout in seconds.
            command_delay: Seconds to wait after each write. Defaults to 0.0 (no
                delay). Some unframed serial instruments (e.g. Tenma/Korad power
                supplies) drop commands or return stale responses if commands are
                sent back-to-back; a small delay paces them.
            dtr: If not None, explicitly drive the DTR line to this state after
                opening the port. Defaults to None (leave pyserial's default behaviour).
            rts: If not None, explicitly drive the RTS line to this state after opening
                the port. Defaults to None.
            dsrdtr: Enable DTR/DSR handshaking. Defaults to False.
            rtscts: Enable RTS/CTS hardware flow control. Defaults to False.
            xonxoff: Enable XON/XOFF software flow control. Defaults to False.

        Raises:
            SerialException: If serial port could not be found.

        """
        super().__init__()

        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self._timeout = timeout
        self.command_delay = command_delay
        self.dtr = dtr
        self.rts = rts
        self.dsrdtr = dsrdtr
        self.rtscts = rtscts
        self.xonxoff = xonxoff
        self.connection = None

        if port is not None:
            self.port = port
        elif visa_resource_name is not None:
            parsed = ResourceName.from_string(visa_resource_name)

            if isinstance(parsed, ASRLInstr):
                self.port = parsed.board
            elif isinstance(parsed, (USBInstr, USBRaw)):
                vid = int(parsed.manufacturer_id, 0)
                pid = int(parsed.model_code, 0)
                serial_number = parsed.serial_number
                self.port = self._find_usb_serial_port(vid, pid, serial_number)
                self.logger.info(f"Found COM port: {self.port}")
            else:
                raise TypeError(
                    "Expected a ASRL or USB VISA resource name, but got "
                    f"{parsed.__class__.__name__}"
                )
        elif vid is None or pid is None:
            raise TypeError(
                "Must provide VID and PID if port, or "
                "visa_resource_name is not provided."
            )
        else:
            self.port = self._find_usb_serial_port(vid, pid, serial_number)
            self.logger.info(f"Found COM port: {self.port}")

    def _find_usb_serial_port(
        self, vid: int, pid: int, serial_number: str | None = None
    ) -> str:
        """Find the USB serial port given the product and vendor IDs.

        Args:
            vid: USB vendor ID.
            pid: USB product ID.
            serial_number: USB serial number.

        Raises:
            SerialException: If serial port could not be found.

        """
        for port in list_ports.comports():
            if (
                port.vid == vid
                and port.pid == pid
                and (serial_number is None or port.serial_number == serial_number)
            ):
                return port.device
        raise SerialException("Could not find COM port")

    def connect(self) -> None:
        """Connect to the serial device.

        Raises:
            SerialException: If serial port could not be found.

        """
        self.connection = Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self._timeout,
            dsrdtr=self.dsrdtr,
            rtscts=self.rtscts,
            xonxoff=self.xonxoff,
        )
        # Explicitly drive the control lines after opening. pyserial's on-open
        # defaults are not reliable across platforms/adapters (and DTR is not
        # asserted on POSIX when dsrdtr is enabled), so honour these when set.
        if self.dtr is not None:
            self.connection.dtr = self.dtr
        if self.rts is not None:
            self.connection.rts = self.rts
        self.clear()

    def disconnect(self) -> None:
        """Disconnect from the serial device."""
        if self.connection and self.connection.is_open:
            self.connection.close()

    def clear(self) -> None:
        """Clear input and output buffers.

        Raises:
            PortNotOpenError: If not connected.

        """
        if not self.connection:
            raise PortNotOpenError()
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()

    def write_bytes(self, data: bytes) -> None:
        """Write raw bytes to the serial device.

        Args:
            data: Data to send as raw bytes.

        Raises:
            PortNotOpenError: If not connected.

        """
        if not self.connection:
            raise PortNotOpenError()
        if self.dsrdtr:
            self._write_with_dsr_handshake(data)
        else:
            self.connection.write(data)
        self.connection.flush()
        # Pace back-to-back commands for instruments that need it (see
        # command_delay); a no-op when command_delay is 0.
        if self.command_delay:
            time.sleep(self.command_delay)

    def _write_with_dsr_handshake(self, data: bytes) -> None:
        """Write ``data`` one byte at a time, pausing while DSR is deasserted.

        pyserial's ``dsrdtr`` flag has no effect on the wire on POSIX: Linux termios
        only implements automatic hardware flow control for RTS/CTS (via
        ``CRTSCTS``); there is no kernel-level equivalent for DSR/DTR.

        Args:
            data: Data to send as raw bytes.

        Raises:
            SerialException: If DSR is not reasserted within the configured timeout.

        """
        if not self.connection:
            raise PortNotOpenError()
        poll_interval = 0.01
        timeout = self.get_timeout()
        for byte in data:
            waited = 0.0
            while not self.connection.dsr:
                time.sleep(poll_interval)
                waited += poll_interval
                if timeout and waited > timeout:
                    raise SerialException(
                        "Timed out waiting for DSR while writing - instrument not"
                        " ready to receive data"
                    )
            self.connection.write(bytes((byte,)))
            self.connection.flush()

    def read_bytes(self) -> bytes:
        """Read raw bytes from the serial device.

        Args:
            data: Data to send as raw bytes.

        Returns:
            bytes: Response from the device as raw bytes.

        Raises:
            PortNotOpenError: If not connected.

        """
        if not self.connection:
            raise PortNotOpenError()
        return self.connection.read_until(expected=self.termination)

    def set_timeout(self, timeout: float) -> None:
        """Set the timeout for serial communication.

        Args:
            timeout: Timeout in seconds.

        """
        if self.connection:
            self.connection.timeout = timeout
        else:
            self._timeout = timeout

    def get_timeout(self) -> float:
        """Get the timeout for serial communication.

        Returns:
            float: Timeout in seconds.

        """
        if self.connection:
            return self.connection.timeout
        else:
            return self._timeout
