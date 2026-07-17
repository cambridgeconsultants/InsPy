import abc
import logging
from types import TracebackType


class TransportBase(abc.ABC):
    """An abstract base class defining a contract for transport mechanisms.

    It requires send and receive methods to be implemented by any concrete subclass.
    """

    termination = b"\n"
    encoding = "ascii"

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.logger = logging.getLogger(f"inspy.{self.__class__.__name__}")

    @abc.abstractmethod
    def connect(self) -> None:
        """Establish connection."""
        pass

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Release the connection."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear buffers."""
        pass

    @abc.abstractmethod
    def write_bytes(self, data: bytes) -> None:
        """Write raw bytes without any formatting or encoding."""
        pass

    @abc.abstractmethod
    def read_bytes(self) -> bytes:
        """Read raw bytes without parsing or decoding."""
        pass

    def __enter__(self) -> "TransportBase":
        """Connect when using context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Disconnect when finished with context manager."""
        self.disconnect()

    def command(self, command: str) -> None:
        """Send a command to the instrument.

        The command (as a string) will be encoded to bytes using `self.encoding` and a
        termination (`self.termination`) will be added.

        Args:
            command: The command

        """
        self.write_bytes(command.encode(self.encoding) + self.termination)

    def read(self) -> str:
        """Read the output from the instrument output buffer.

        The read bytes will be decoded (using `self.encoding`) and then stripped of
        leading and trailing whitespace.

        Returns:
            Instrument Output.

        """
        return self.read_bytes().decode(self.encoding).strip()

    def query(self, command: str) -> str:
        """Send a command and receive a result.

        The command will be sent using :obj:`~TransportBase.command` (i.e. with
        encoding and termination) and then a read performed. The read bytes will be
        decoded (using `self.encoding`) and then stripped of leading and trailing
        whitespace.

        Args:
            command: The command

        """
        self.command(command)
        return self.read()

    @abc.abstractmethod
    def set_timeout(self, timeout: float) -> None:
        """Set transport timeout.

        Args:
            timeout: Timeout in seconds.

        """
        pass

    @abc.abstractmethod
    def get_timeout(self) -> float:
        """Get transport timeout.

        Returns:
            Timeout in seconds.

        """
        pass

    def set_encoding(self, encoding: str) -> None:
        """Set transport encoding.

        Args:
            encoding: The encoding to use.

        """
        self.encoding = encoding

    def set_termination(self, termination: str) -> None:
        """Set termination character.

        Args:
            termination: The termination character.

        """
        self.termination = termination.encode(self.encoding)
