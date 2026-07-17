"""Agilent digital multimeter classes."""

from .keysight_dmm import DmmKeysight344xxA

# Temporarily until it is tested. Maybe rename and move DmmKeysight344xxA into base


class DmmAgilent34410A(DmmKeysight344xxA):
    """Agilent 34410A digital multimeter class. Untested.

    Based on Keysight 344xxA class.

    Inherits all methods from the DmmKeysight34465A class, and
    adds none.

    `Agilent 34410A User Manual <https://www.keysight.com/gb/en/assets/9018-05586/user-manuals/9018-05586.pdf?success=true>`_
    """  # noqa E501

    pass
