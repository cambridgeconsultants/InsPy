"""Send large USBTMC Bulk-OUT writes as a single message on the pyvisa-py backend.

pyvisa-py (0.8.1) splits an outgoing write into one ``DEV_DEP_MSG_OUT`` message
per ``wMaxPacketSize`` bytes of the Bulk-OUT endpoint (``USBTMC.write``). For a
USB full-speed instrument such as the Agilent 33220A that is only 64 bytes, so a
single SCPI command longer than 64 bytes is delivered as many separate USBTMC
messages (``EOM`` set on the last one).

A command like ``DATA VOLATILE, <comma separated samples>`` from
``set_new_arbitrary_waveform`` is tens of kilobytes, which becomes hundreds of
fragmented messages. The 33220A's USBTMC firmware does not reliably reassemble
one logical command split this way, so the transfer breaks. This is Linux-only
in practice because vendor VISA libraries (Keysight, NI) — used on Windows —
send the command as a single Bulk-OUT message (one header, full
``TransferSize``, data streamed across USB packets by the host controller),
which is what the device expects. pyvisa-py ``main`` chunks identically, so an
upstream upgrade does not address this.

Calling :func:`apply` patches pyvisa-py so ``USBTMC.write`` builds one Bulk-OUT
message for the whole payload, matching vendor VISA behaviour. The patched class
is only exercised when the pyvisa-py backend is selected at runtime, so other
backends are unaffected.

References:
    USBTMC 1.00 section 3.2 (DEV_DEP_MSG_OUT / Bulk-OUT transfers).
"""

from pyvisa_py.protocols.usbtmc import USBTMC, BulkOutMessage, USBRaw


def _usbtmc_write(self: USBTMC, data: bytes) -> int:
    """Send ``data`` as a single USBTMC Bulk-OUT message.

    Wraps the entire payload in one ``DEV_DEP_MSG_OUT`` (``EOM`` set) and writes
    it in a single Bulk-OUT transfer; the host controller packetises it into
    ``wMaxPacketSize`` USB packets. This avoids pyvisa-py's per-packet
    fragmentation, which some instruments cannot reassemble. Returns the number
    of payload bytes sent.
    """
    # bTag advances per transfer, exactly as pyvisa-py's own write does.
    self._btag = (self._btag % 255) + 1
    # USBRaw.write performs the Bulk-OUT transfer and translates a
    # usb.core.USBError into a ValueError, matching pyvisa-py's own write.
    USBRaw.write(self, BulkOutMessage.build_array(self._btag, True, data))
    return len(data)


def apply() -> None:
    """Patch pyvisa-py so USBTMC writes are sent as a single Bulk-OUT message.

    Safe to call multiple times; a no-op once the patch is installed.
    """
    if USBTMC.write is not _usbtmc_write:
        USBTMC.write = _usbtmc_write  # ty: ignore[invalid-assignment]
