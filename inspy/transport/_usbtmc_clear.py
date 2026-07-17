"""Add USBTMC device clear (``viClear``) support to the pyvisa-py backend.

pyvisa-py (0.8.1) does not implement ``viClear`` for USB sessions:
``pyvisa_py.sessions.Session.clear`` returns ``error_nonsupported_operation``
and ``USBSession`` never overrides it. The ``initiate_clear`` /
``check_clear_status`` USBTMC request codes are defined but unused. As a result
``Resource.clear()`` is a silent no-op on this backend.

This matters for recovery from timeouts. A Keysight oscilloscope left
mid-``:DIGitize`` (e.g. a trigger timeout in ``NORM`` sweep) blocks its command
parser, so a queued ``*CLS`` / ``:STOP`` never runs. The only way to abort the
acquisition is a USBTMC device clear. Vendor VISA libraries (Keysight, NI)
implement this, which is why the same code recovers there; on pyvisa-py the
scope hangs until it is power-cycled.

Calling :func:`apply` patches pyvisa-py (unless it already provides a working
clear) so that ``Resource.clear()`` performs a real device clear. The patched
classes are only ever exercised when the pyvisa-py backend is selected at
runtime, so other backends are unaffected.

References:
    USBTMC 1.00 sections 4.2.1.6 (INITIATE_CLEAR) and 4.2.1.7
    (CHECK_CLEAR_STATUS).
"""

import time

import usb.core
import usb.util
from pyvisa.constants import StatusCode
from pyvisa_py.protocols.usbtmc import USBTMC, Request, UsbTmcStatus
from pyvisa_py.usb import USBSession

#: Maximum number of CHECK_CLEAR_STATUS polls before giving up.
_CLEAR_STATUS_RETRIES = 100
#: bmClear bit D0 in a CHECK_CLEAR_STATUS response: the device has queued
#: Bulk-IN data the host must read out before re-checking (USBTMC 1.00 4.2.1.7).
_BM_CLEAR_BULK_IN_DATA = 0x01


def _usbtmc_clear(self: USBTMC) -> None:
    """Perform a USBTMC device clear on the instrument.

    Issues ``INITIATE_CLEAR`` then polls ``CHECK_CLEAR_STATUS`` until the device
    reports the clear is complete, and finally clears the Bulk-OUT halt so the
    next write starts from a clean state.

    Raises:
        usb.core.USBError: If the device refuses the ``INITIATE_CLEAR`` request,
            reports a failure status, or has not finished clearing after
            ``_CLEAR_STATUS_RETRIES`` polls. ``_usbsession_clear`` translates
            this into a VISA status code.

    """
    # INITIATE_CLEAR (USBTMC 1.00 4.2.1.6):
    #   wValue = 0x0000, wIndex = interface, wLength = 0x0001.
    data = self.usb_dev.ctrl_transfer(
        usb.util.build_request_type(
            usb.util.CTRL_IN,
            usb.util.CTRL_TYPE_CLASS,
            usb.util.CTRL_RECIPIENT_INTERFACE,
        ),
        Request.initiate_clear,
        0x0000,
        self.usb_intf.index,
        0x0001,
        timeout=self.timeout,
    )
    if data[0] != UsbTmcStatus.success:
        raise usb.core.USBError("USBTMC INITIATE_CLEAR was refused by the device")

    # CHECK_CLEAR_STATUS (USBTMC 1.00 4.2.1.7): poll the device until the clear
    # completes. The response is two bytes: data[0] is the USBTMC status and
    # data[1] is bmClear.
    #   - success: the clear has finished.
    #   - pending: still clearing. If bmClear bit D0 is set, the device has
    #     queued Bulk-IN data that the host must read out before re-polling;
    #     otherwise just wait and poll again.
    #   - anything else: the clear failed.
    #   wValue = 0x0000, wIndex = interface, wLength = 0x0002.
    for _ in range(_CLEAR_STATUS_RETRIES):
        data = self.usb_dev.ctrl_transfer(
            usb.util.build_request_type(
                usb.util.CTRL_IN,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE,
            ),
            Request.check_clear_status,
            0x0000,
            self.usb_intf.index,
            0x0002,
            timeout=self.timeout,
        )
        match data[0]:
            case UsbTmcStatus.success:
                break
            case UsbTmcStatus.pending:
                if data[1] & _BM_CLEAR_BULK_IN_DATA:
                    _drain_bulk_in(self)
                else:
                    time.sleep(0.05)
            case _:
                raise usb.core.USBError("USBTMC device clear failed")
    else:
        raise usb.core.USBError("USBTMC device clear did not complete")

    # Clear the Bulk-OUT halt so subsequent writes are not stalled.
    self.usb_send_ep.clear_halt()


def _drain_bulk_in(self: USBTMC) -> None:
    """Read and discard queued Bulk-IN data until a short packet is received.

    Per USBTMC 1.00 4.2.1.7, when ``CHECK_CLEAR_STATUS`` reports the clear is
    pending with the Bulk-IN-data bit set, the host must flush whatever the
    device queued on the Bulk-IN endpoint (e.g. a partial response abandoned by
    the cleared command) before checking again. A short read (including a USB
    timeout once the endpoint is empty) marks the end of the queued data.
    """
    endpoint = self.usb_recv_ep
    max_packet = endpoint.wMaxPacketSize
    while True:
        try:
            chunk = endpoint.read(max_packet, self.timeout)
        except usb.core.USBError:
            return
        if len(chunk) < max_packet:
            return


def _usbsession_clear(self: USBSession) -> StatusCode:
    """Clear the device, corresponding to ``viClear``.

    Delegates to the interface's device clear when available (USBTMC) and
    reports the outcome as a VISA status code, matching the convention used by
    pyvisa-py's other session ``clear`` implementations (which return a status
    code rather than raising).

    Returns:
        ``StatusCode.success`` on success, ``error_nonsupported_operation`` if
        the interface has no device clear (e.g. a raw USB interface), or
        ``error_io`` if the device clear fails.

    """
    interface_clear = getattr(self.interface, "clear", None)
    if interface_clear is None:
        return StatusCode.error_nonsupported_operation
    try:
        interface_clear()
    except usb.core.USBError:
        return StatusCode.error_io
    return StatusCode.success


def apply() -> None:
    """Patch pyvisa-py to support USBTMC device clear, if needed.

    Safe to call multiple times and a no-op if pyvisa-py already provides a USB
    ``clear`` (e.g. a future release that fixes this upstream).
    """
    # Only patch if pyvisa-py does not already define its own clear, so we defer
    # to an upstream fix once one exists.
    if "clear" not in vars(USBTMC):
        USBTMC.clear = _usbtmc_clear  # ty: ignore[unresolved-attribute]
    if "clear" not in vars(USBSession):
        USBSession.clear = _usbsession_clear  # ty: ignore[invalid-assignment]
