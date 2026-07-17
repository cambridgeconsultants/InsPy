"""Add serial device clear (``viClear``) support to the pyvisa-py backend.

pyvisa-py (0.8.1) does not implement ``viClear`` for serial (ASRL) sessions:
``pyvisa_py.serial.SerialSession`` defines ``flush`` but no ``clear``, so it
inherits ``pyvisa_py.sessions.Session.clear`` which returns
``error_nonsupported_operation``. Unlike the USB case, pyvisa routes the serial
``clear`` return code through ``handle_return_value``, which raises on any
negative status — so ``Resource.clear()`` raises ``VisaIOError`` (NSUP_OPER)
rather than being a no-op.

This breaks every serial instrument on this backend: ``PyVisaTransport.connect``
calls ``self.clear()`` immediately after opening, so the connection raises
before the device is ever used. It is Linux-only in practice because vendor VISA
libraries (Keysight, NI) — used on Windows — implement serial ``viClear``.

Calling :func:`apply` patches pyvisa-py (unless it already provides a working
clear) so that ``Resource.clear()`` discards the serial input and output
buffers, matching what a serial device clear means (and what
:class:`~inspy.transport.serial_transport.SerialTransport.clear` does). The
patched class is only exercised when the pyvisa-py backend is selected at
runtime, so other backends are unaffected.
"""

from pyvisa.constants import StatusCode
from pyvisa_py.serial import SerialSession
from serial import SerialException


def _serial_clear(self: SerialSession) -> StatusCode:
    """Clear the device, corresponding to ``viClear``.

    Discards the serial input and output buffers and reports the outcome as a
    VISA status code, matching the convention used by pyvisa-py's session
    methods (which return a status code rather than raising).

    Returns:
        ``StatusCode.success`` on success, or ``error_io`` if the underlying
        pyserial call fails.

    """
    try:
        self.interface.reset_input_buffer()
        self.interface.reset_output_buffer()
    except SerialException:
        return StatusCode.error_io
    return StatusCode.success


def apply() -> None:
    """Patch pyvisa-py to support serial device clear, if needed.

    Safe to call multiple times and a no-op if pyvisa-py already provides a
    serial ``clear`` (e.g. a future release that fixes this upstream).
    """
    # Only patch if SerialSession does not define its own clear, so we defer to
    # an upstream fix once one exists.
    if "clear" not in vars(SerialSession):
        SerialSession.clear = _serial_clear  # ty: ignore[invalid-assignment]
