import abc
import inspect
import logging
import weakref
from collections.abc import Callable
from functools import wraps
from types import FrameType, TracebackType
from typing import Any, TypeVar, cast

from pyvisa.errors import VisaIOError

from inspy.transport import PyVisaTransport, SerialTransport, TransportBase

F = TypeVar("F", bound=Callable[..., Any])
_TInstrument = TypeVar("_TInstrument", bound="InstrumentBase")


def _cleanup(transport: TransportBase) -> None:
    """Handle instruments going out of scope."""
    try:
        transport.disconnect()
    except Exception:
        pass


def _repr_truncated(obj: object, max_length: int = 20, ellipsis: str = "...") -> str:
    """Repr, but with truncation."""
    # Try and truncate the data to avoid running repr on large data
    try:
        obj = cast("Any", obj)[:max_length]
    except TypeError:
        pass
    st = repr(obj)
    if len(st) > max_length:
        st = st[: max_length - len(ellipsis)] + ellipsis
    return st


def _log_method_call(func: F) -> F:
    """Add logging to decorated function.

    This logs the class name, method name and args before the call and the result after
    the call. All values are converted to a string using repr and truncated to reduce
    log clutter.

    NOTE: that this only logs calls from outside of the class to reduce log clutter.
    """

    @wraps(func)
    def wrapper(self: "InstrumentBase", *args: object, **kwargs: object) -> F:
        # Check if called from within the instrument. There's possibly a better way to
        # do this, but checking if the caller has a local variable `self`` that matches
        # the `self`` of the method call seems to work.

        # Allow disabling the logging by setting auto_log_level to logging.NOTSET
        log_enabled = self.auto_log_level != logging.NOTSET

        # Check call was external to the class
        if log_enabled:
            current_frame = inspect.currentframe()
            assert isinstance(current_frame, FrameType)
            caller_frame = current_frame.f_back
            assert isinstance(caller_frame, FrameType)
            log_enabled = not caller_frame.f_locals.get("self", None) == self

        # Log method call before running
        if log_enabled:
            class_name = self.__class__.__name__
            method_name = func.__name__
            arg_st = ", ".join(
                [f"{_repr_truncated(arg_value)}" for arg_value in args]
                + [
                    f"{arg_name}={_repr_truncated(arg_value)}"
                    for arg_name, arg_value in kwargs.items()
                ]
            )
            self.logger.log(
                self.auto_log_level, f"{class_name}.{method_name}({arg_st})"
            )

        # Run method
        result = func(self, *args, **kwargs)

        # Log result
        if log_enabled and result is not None:
            self.logger.log(
                self.auto_log_level,
                f"{class_name}.{method_name} -> {_repr_truncated(result)}",
            )

        return result

    return cast("F", wrapper)


class _InstrumentMeta(abc.ABCMeta):
    """Meta class to add logging of calls to instrument methods."""

    def __new__(
        mcs: "type[_InstrumentMeta]",
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, object],
    ) -> type:
        for key in attrs.keys():
            if not key.startswith("_") and callable(attrs[key]):
                attrs[key] = _log_method_call(cast("Callable[..., Any]", attrs[key]))
        return super().__new__(mcs, name, bases, attrs)


class InstrumentBase(metaclass=_InstrumentMeta):
    """Instrument Base class.

    This class should be subclassed by all instrument classes.
    It provides basic functionality for connecting and disconnecting from the
    instrument.
    """

    auto_log_level: int = logging.INFO
    """The log level used for automatic logging of method calls.

    To disable logging set to `logging.NOTSET`.
    """

    def __init__(self, transport: TransportBase) -> None:
        self.transport: TransportBase = transport
        self.is_connected: bool = False
        self.logger: logging.Logger = logging.getLogger(
            f"inspy.{self.__class__.__name__}"
        )
        self._finalizer = weakref.finalize(self, _cleanup, transport)

    def connect(self) -> None:
        """Connect to instrument using the transport layer."""
        self.transport.connect()
        self.is_connected = True

    def disconnect(self) -> None:
        if self.is_connected:
            self.transport.disconnect()
        self.is_connected = False
        self._finalizer.detach()

    def __enter__(self: _TInstrument) -> _TInstrument:
        """Connect (using transport layer) when using context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Disconnect (using transport layer) when finished with context manager."""
        self.disconnect()

    def get_id(self) -> str:
        """Identification Query.

        Returns:
            Instrument Identification String.

        """
        return self.transport.query("*IDN?")

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset instrument to factory default state, including clearing status.

        Example implementation:
            >>> self.transport.clear()
            >>> self.transport.command("*CLS")
            >>> self.transport.command("*RST")
        """
        pass

    @abc.abstractmethod
    def await_completion(self) -> None:
        """Configure the instrument to wait for all pending operations.

        Example implementation:
            >>> self.transport.query("*OPC?")
        Or if supported:
            >>> self.transport.command("*WAI")
        """
        pass


class VisaInstrumentMixin(InstrumentBase):
    """Mixin adding VISA-address construction to an instrument.

    Mix into an :class:`InstrumentBase` subclass. Builds a
    :class:`PyVisaTransport` from a VISA address, or accepts a ready-made
    ``transport``.
    """

    transport: PyVisaTransport

    def __init__(
        self,
        visa_address: str | None = None,
        transport: PyVisaTransport | None = None,
    ) -> None:
        if transport is None:
            if visa_address is None:
                raise ValueError("One of 'visa_address' or 'transport' is required.")
            transport = PyVisaTransport(visa_address)
        super().__init__(transport)


class SerialInstrumentMixin(InstrumentBase):
    """Mixin adding serial-address construction to an instrument.

    Mix into an :class:`InstrumentBase` subclass. Builds a
    :class:`SerialTransport` from a VISA resource name, or accepts a ready-made
    ``transport``. Subclasses can override this to configure serial settings
    (e.g. baudrate, parity).
    """

    transport: SerialTransport

    def __init__(
        self,
        visa_address: str | None = None,
        transport: SerialTransport | None = None,
    ) -> None:
        if transport is None:
            if visa_address is None:
                raise ValueError("One of 'visa_address' or 'transport' is required.")
            transport = SerialTransport(visa_resource_name=visa_address)
        super().__init__(transport)


class InstrumentError(Exception):
    """Error class raised when errors are reported by the instrument."""

    def __init__(self, errors: list[tuple[int, str]]) -> None:
        self.errors: list[tuple[int, str]] = errors

        description = ", ".join(
            [
                f"[{error_num}] {error_description}"
                for error_num, error_description in errors
            ]
        )
        super().__init__(description)


class ErrorCheckedInstrumentMixin(InstrumentBase):
    """Mixin adding SCPI error checking and completion awaiting to an instrument.

    Mix into an :class:`InstrumentBase` subclass alongside a transport mixin
    (:class:`VisaInstrumentMixin` or :class:`SerialInstrumentMixin`). Combine with
    the :func:`with_check` decorator to have methods await completion and raise
    ``_error_class`` if the instrument reports any errors.
    """

    _error_class: type[InstrumentError] = InstrumentError
    """The exception type raised by :func:`with_check` when errors are reported.

    Override in a subclass to raise an instrument-family-specific error type.
    """

    def get_errors(self) -> list[tuple[int, str]]:
        """Get a list of errors and error numbers from the instrument.

        Returns:
            A list where each value is a tuple of the error number and error
            description

        """
        errors = []
        while True:
            response = self.transport.query(":SYSTem:ERRor?")
            error_num_st, _, error_description_st = response.partition(",")
            error_num = int(error_num_st)
            error_description = error_description_st.strip('"')
            if error_num != 0:
                errors.append((error_num, error_description))
            else:
                break
        return errors

    def await_completion(self) -> None:
        """Wait for the instrument to complete the current operation."""
        self.transport.query("*OPC?")


def with_check(func: F) -> F:
    """Add completion and error checking to a method.

    The owning class must mix in :class:`ErrorCheckedInstrumentMixin`.
    """

    @wraps(func)
    def wrapper(
        self: "ErrorCheckedInstrumentMixin", *args: object, **kwargs: object
    ) -> object:
        try:
            result = func(self, *args, **kwargs)
            self.await_completion()
            return result
        except VisaIOError as ex:
            # To prevent timeouts from blocking subsequent commands
            # (e.g., setting a trigger too high),
            # Clear the output buffer and reset the status.
            self.transport.clear()
            self.transport.command("*CLS")
            raise ex from None
        finally:
            errors = self.get_errors()
            if errors:
                raise self._error_class(errors)

    return cast("F", wrapper)
