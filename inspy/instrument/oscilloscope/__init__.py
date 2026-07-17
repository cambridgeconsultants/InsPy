"""Oscilloscope interfaces."""

from ._base import OscilloscopeError
from .agilent_oscilloscope import (
    OscilloscopeAgilentDSO6012A,
)
from .keysight_oscilloscope import (
    OscilloscopeKeysightDSOX1102G,
    OscilloscopeKeysightDSOX1202G,
    OscilloscopeKeysightDSOX2024A,
)

__all__: list[str] = [
    "OscilloscopeError",
    "OscilloscopeAgilentDSO6012A",
    "OscilloscopeKeysightDSOX1102G",
    "OscilloscopeKeysightDSOX1202G",
    "OscilloscopeKeysightDSOX2024A",
]
