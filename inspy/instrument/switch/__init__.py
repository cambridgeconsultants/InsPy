"""Switches Interfaces.

This group includes the following type of switches:

- Mains Switch
  - TBD
- Optical Switch
  - TBD
- RF Switch
  - TBD
- Relay
  - TBD
"""

from .thorlabs_optical_switch import OpticalSwitchThorlabsOSW12

__all__: list[str] = ["OpticalSwitchThorlabsOSW12"]
