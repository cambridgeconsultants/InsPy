"""Tests of the SCPI commands sent by the Keysight 344xxA multimeter class.

These tests use a mock transport, so they run without an instrument attached.
"""

from unittest.mock import MagicMock

import pytest

from inspy.instrument.digitalmultimeter.keysight_dmm import DmmKeysight34465A

REPLIES = {"*OPC?": "1", ":SYSTem:ERRor?": '+0,"No error"'}


def make_dmm(function: str) -> tuple[DmmKeysight34465A, MagicMock]:
    """Make a multimeter on a mock transport with ``function`` as the active function.

    The mock reports no errors and answers ``CONF?`` the way the instrument does.
    """
    replies = {**REPLIES, "CONF?": f'"{function} +1.00000000E+01,+3.00000000E-06"'}
    transport = MagicMock()
    transport.query.side_effect = replies.__getitem__
    return DmmKeysight34465A(transport=transport), transport


def commands_sent(transport: MagicMock) -> list[str]:
    """Get the commands sent to the mock transport, in order."""
    return [call.args[0] for call in transport.command.call_args_list]


@pytest.mark.parametrize("function", ["VOLT", "CURR", "RES", "FRES", "TEMP"])
def test_set_averaging_time_uses_active_function(function: str) -> None:
    dmm, transport = make_dmm(function)

    dmm.set_averaging_time(averaging_time=0.5)

    assert commands_sent(transport) == [
        f"{function}:APER:ENAB 1",
        f"{function}:APER 0.5",
    ]


def test_set_averaging_time_rejects_unsupported_function() -> None:
    dmm, transport = make_dmm("CAP")

    with pytest.raises(Exception, match="only supported by"):
        dmm.set_averaging_time(averaging_time=1)

    assert commands_sent(transport) == []
