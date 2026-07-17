"""Transport layer for using PyVisa."""

import logging
import socket
from collections.abc import Callable, Iterable, Sequence
from typing import Any, overload

from pyvisa import ResourceManager
from pyvisa.resources import TCPIPSocket
from pyvisa.resources.messagebased import MessageBasedResource
from pyvisa.util import BINARY_DATATYPES, from_ieee_block, to_ieee_block

from . import _serial_clear, _usbtmc_clear, _usbtmc_write
from ._base import TransportBase

# pyvisa-py does not implement viClear for USB, so Resource.clear() is a no-op
# there. Without it, an instrument left mid-acquisition (e.g. a trigger timeout)
# cannot be recovered in software. This restores a working device clear.
_usbtmc_clear.apply()

# pyvisa-py does not implement viClear for serial (ASRL) sessions, where it
# raises VI_ERROR_NSUP_OPER rather than being a no-op. connect() calls clear()
# right after opening, so without this every serial instrument fails to connect.
# This makes a serial clear flush the input/output buffers.
_serial_clear.apply()

# pyvisa-py splits a Bulk-OUT write into one USBTMC message per wMaxPacketSize
# bytes, which some instruments (e.g. the Agilent 33220A) cannot reassemble for
# large commands such as an arbitrary waveform upload. This sends the whole
# payload as a single Bulk-OUT message, matching vendor VISA behaviour.
_usbtmc_write.apply()

rm = ResourceManager()

logger = logging.getLogger(__name__)


class PyVisaTransport(TransportBase):
    """Transport layer for using pyvisa."""

    termination = b"\r\n"
    CHUNK_SIZE = 102400  # 5 * 20480 (pyvisa default chunk size)
    resource: MessageBasedResource

    def __init__(self, visa_address: str) -> None:
        """Initialize PyVisaTransport.

        Args:
            visa_address: The VISA address.

        """
        self.visa_address = visa_address
        super().__init__()

    def connect(self) -> None:
        """Connect to the instrument."""
        # Open resource with timeout of 5000 ms.
        resource = rm.open_resource(self.visa_address, timeout=5000, open_timeout=5000)

        if not isinstance(resource, MessageBasedResource):
            raise TypeError(
                f"Expected MessageBasedResource, but got {resource.__class__.__name__}"
            )

        # Raw TCP sockets need an explicit read terminator, and Nagle disabled
        if isinstance(resource, TCPIPSocket):
            resource.read_termination = "\n"

            # Nagle needs to be disabled for small SCPI messages. The Keysight backend
            # is expected to handle this, but PyVISA-py doesn't.
            sessions = getattr(resource.visalib, "sessions", None)
            if sessions is not None:
                try:
                    sock = sessions[resource.session].interface
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except (AttributeError, KeyError, OSError):
                    logger.warning(
                        f"Could not disable Nagle on {resource.resource_name}, this "
                        "may cause read timeouts",
                    )

        self.resource = resource

        self.clear()

    def disconnect(self) -> None:
        """Disconnect from the instrument."""
        self.resource.close()

    def clear(self) -> None:
        """Clear buffers."""
        self.resource.clear()

    def write_bytes(self, data: bytes) -> None:
        """Write raw bytes without any formatting or encoding."""
        self.resource.write_raw(data)

    def read_bytes(self) -> bytes:
        """Read raw bytes without parsing or decoding."""
        return self.resource.read_raw(size=self.CHUNK_SIZE)

    def _read_block_data(self) -> bytes:
        """Read a complete IEEE 488.2 definite-length block.

        pyvisa-py's USBTMC read returns at most one ``read_raw`` chunk rather
        than reading to the end of the message, so a block larger than the
        chunk size (e.g. an oscilloscope waveform) arrives split across several
        reads. This is why a large transfer fails on the pyvisa-py (Linux)
        backend but not on a vendor VISA library, which reads to end-of-message.
        The ``#<n><length>`` block header gives the exact data length, so this
        keeps reading until the whole block has been received.

        Returns:
            The complete block, header included, ready for ``from_ieee_block``.

        """
        buf = bytearray(self.resource.read_raw(size=self.CHUNK_SIZE))

        # A definite-length block starts with '#', a single digit n, then n
        # digits giving the number of data bytes. Anything else (e.g. an
        # indefinite '#0' block) is left for the parser to handle as-is.
        if not (len(buf) >= 2 and buf[:1] == b"#" and buf[1:2].isdigit()):
            return bytes(buf)
        n = int(buf[1:2])
        if n == 0:
            return bytes(buf)

        header_len = 2 + n
        while len(buf) < header_len:
            chunk = self.resource.read_raw(size=self.CHUNK_SIZE)
            if not chunk:
                return bytes(buf)
            buf += chunk

        data_len = int(buf[2:header_len])
        while len(buf) < header_len + data_len:
            chunk = self.resource.read_raw(size=self.CHUNK_SIZE)
            if not chunk:
                break
            buf += chunk
        return bytes(buf)

    def set_timeout(self, timeout: float) -> None:
        """Set PyVisa timeout.

        Args:
            timeout: Timeout in seconds.

        """
        self.resource.timeout = timeout * 1000.0

    def get_timeout(self) -> float:
        """Get PyVisa timeout value.

        Returns:
            Timeout value in seconds.

        """
        return self.resource.timeout / 1000.0

    def command_with_block_data(
        self,
        command: str,
        items: Sequence[int | float],
        data_type: BINARY_DATATYPES = "B",
        is_big_endian: bool = False,
    ) -> None:
        """Send a command with encoded data.

        Args:
            command: The command
            items: Items of data to be encoded
            data_type: `struct style format <https://docs.python.org/3/library/struct.html#format-characters>`_
                used for items.
            is_big_endian: Endian.

        """  # noqa: E501
        self.write_bytes(
            command.encode(self.encoding)
            + b" "
            + to_ieee_block(items, data_type, is_big_endian)
            + self.termination
        )

    @overload
    def query_for_block_data(
        self,
        command: str,
        data_type: BINARY_DATATYPES = ...,
        container: type[bytes] = ...,
        is_big_endian: bool = ...,
    ) -> bytes: ...

    @overload
    def query_for_block_data(
        self,
        command: str,
        data_type: BINARY_DATATYPES,
        container: Callable[[Iterable[int | float]], Sequence[int | float]],
        is_big_endian: bool = ...,
    ) -> Sequence[int | float]: ...

    def query_for_block_data(
        self,
        command: str,
        data_type: BINARY_DATATYPES = "B",
        container: Any = bytes,  # noqa: ANN401
        is_big_endian: bool = False,
    ) -> bytes | Sequence[int | float]:
        """Query for encoded data.

        Args:
            command: The command
            data_type: `struct style format <https://docs.python.org/3/library/struct.html#format-characters>`_
                used received items.
            container: The type used to hold the items. Defaults to ``bytes``.
                Pass a callable such as ``list`` to get a ``Sequence[int | float]``.
            is_big_endian: Endian.

        """  # noqa: E501
        self.command(command)
        return from_ieee_block(
            self._read_block_data(), data_type, is_big_endian, container
        )

    def query_with_block_data_for_block_data(
        self,
        command: str,
        items: Sequence[int | float],
        command_data_type: BINARY_DATATYPES = "B",
        result_data_type: BINARY_DATATYPES = "B",
        result_container: Any = bytes,  # noqa: ANN401
        is_big_endian: bool = False,
    ) -> Sequence[int | float]:
        """Query with encoded data and also receive encoded data.

        Args:
            command: The command.
            items: Items of data to be encoded for sending.
            command_data_type: `struct style format` used for items to send.
                See `struct format characters <https://docs.python.org/3/library/struct.html#format-characters>`_
                for details.
            result_data_type: `struct style format` used for received items.
                See `struct format characters <https://docs.python.org/3/library/struct.html#format-characters>`_
                for details.
            result_container: The type used to hold received items (e.g., list).
            is_big_endian: Endian.

        """  # noqa: E501
        self.command_with_block_data(command, items, command_data_type, is_big_endian)
        return from_ieee_block(
            self._read_block_data(), result_data_type, is_big_endian, result_container
        )
