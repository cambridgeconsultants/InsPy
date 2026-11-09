"""Tests of the SCPI commands sent by the Keysight power supply class.

These tests use a mock transport, so they run without an instrument attached.
"""

from unittest.mock import MagicMock

import pytest

from inspy.instrument.powersupply.keysight_psu import PsuKeysightE36312A

REPLIES = {"*OPC?": "1", ":SYSTem:ERRor?": '+0,"No error"'}


def make_psu() -> tuple[PsuKeysightE36312A, MagicMock]:
    """Make a power supply on a mock transport that reports no errors."""
    transport = MagicMock()
    transport.query.side_effect = REPLIES.__getitem__
    return PsuKeysightE36312A(transport=transport), transport


def commands_sent(transport: MagicMock) -> list[str]:
    """Get the commands sent to the mock transport, in order."""
    return [call.args[0] for call in transport.command.call_args_list]


@pytest.mark.parametrize("channel", [1, 2, 3])
@pytest.mark.parametrize("enable", [True, False])
def test_set_current_protection_state_uses_requested_channel(
    channel: int, enable: bool
) -> None:
    psu, transport = make_psu()

    psu.set_current_protection_state(enable=enable, channel=channel)

    assert commands_sent(transport) == [
        f"OUTP 0,(@{channel})",
        f"CURR:PROT:STAT {1 if enable else 0},(@{channel})",
    ]


@pytest.mark.parametrize("channel", [1, 2, 3])
def test_reset_current_trip_with_disable_uses_requested_channel(channel: int) -> None:
    psu, transport = make_psu()

    psu.reset_current_trip_with_disable(channel=channel)

    assert commands_sent(transport) == [
        f"OUTP 0,(@{channel})",
        f"CURR:PROT:CLE (@{channel})",
    ]
