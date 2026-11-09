"""Tests of the SCPI commands sent by the Keysight 2000X series scope class.

These tests use a mock transport, so they run without an instrument attached.
"""

from unittest.mock import MagicMock

import pytest

from inspy.instrument.oscilloscope.keysight_oscilloscope import (
    OscilloscopeKeysightDSOX1202G,
    OscilloscopeKeysightDSOX2024A,
)


def make_scope(
    scope_class: type[OscilloscopeKeysightDSOX2024A | OscilloscopeKeysightDSOX1202G],
) -> tuple[OscilloscopeKeysightDSOX2024A | OscilloscopeKeysightDSOX1202G, MagicMock]:
    """Make a scope of the given class on a mock transport."""
    transport = MagicMock()
    return scope_class(transport=transport), transport


def commands_sent(transport: MagicMock) -> list[str]:
    """Get the commands sent to the mock transport, in order."""
    return [call.args[0] for call in transport.command.call_args_list]


@pytest.mark.parametrize("mode", ["EDGE", "DEL", "EBUR", "OR", "RUNT", "USB"])
def test_2000x_set_trigger_mode_accepts_the_modes_it_documents(mode: str) -> None:
    scope, transport = make_scope(OscilloscopeKeysightDSOX2024A)

    scope.set_trigger_mode(mode)

    assert commands_sent(transport) == [f":TRIGger:MODE {mode}"]


@pytest.mark.parametrize(
    "scope_class", [OscilloscopeKeysightDSOX2024A, OscilloscopeKeysightDSOX1202G]
)
def test_set_trigger_mode_rejects_an_unknown_mode(
    scope_class: type[OscilloscopeKeysightDSOX2024A | OscilloscopeKeysightDSOX1202G],
) -> None:
    scope, transport = make_scope(scope_class)

    with pytest.raises(ValueError, match="is not a valid value"):
        scope.set_trigger_mode("NOT_A_MODE")

    assert commands_sent(transport) == []


def test_1200x_set_trigger_mode_still_rejects_a_2000x_only_mode() -> None:
    scope, transport = make_scope(OscilloscopeKeysightDSOX1202G)

    with pytest.raises(ValueError, match="is not a valid value"):
        scope.set_trigger_mode("RUNT")

    assert commands_sent(transport) == []
