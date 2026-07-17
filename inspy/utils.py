"""Utility functions for InsPy."""

import importlib
import inspect
import pkgutil
from collections.abc import Callable, Generator, Sequence
from functools import wraps
from inspect import getmembers, isclass, isfunction
from types import ModuleType
from typing import Literal, TypeVar, cast

import pyvisa
from pyvisa.resources import MessageBasedResource

_F = TypeVar("_F", bound=Callable[..., object])


def validate_args(**rules: Sequence[str | int]) -> Callable[[_F], _F]:
    """Validate arguments against a list of allowed values.

    This will also be used to validate the allowed values for the arguments. Either
    specify a list of values or the name of a class attribute containing the values.

    Usage:
    >>> @validate_args(channel='channels', arg1=['x', 'y', 'z'], arg2=['a', 'b', 'c'])
    >>> def my_func(self, channel, arg1, arg2):
    >>>    '''My function
    >>>
    >>>     Args:
    >>>         channel (1 | 2 | 3 | 4): Channel number
    >>>         arg1 ('x' | 'y' | 'z'): Argument 1
    >>>         arg2 ('a' | 'b' | 'c'): Argument 2
    >>>     '''
    """

    def decorator(func: _F) -> _F:
        # For validating the allowed values
        func._allowed_values = rules  # type: ignore[attr-defined]

        @wraps(func)
        def wrapper(self: object, *args: object, **kwargs: object) -> object:
            # Validate calls to the function

            # Get the full set of arguments including defaults from the call
            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()

            # For each of the rules...
            for arg_name, allowed_values in rules.items():
                # Get the value of the argument in the call
                arg_value = bound_args.arguments[arg_name]

                # If the rule is a string assume it's the name of a class attribute
                if isinstance(allowed_values, str):
                    allowed_values = getattr(self, allowed_values)

                # Check that the value is valid
                if arg_value not in allowed_values:
                    raise ValueError(
                        f"{arg_value!r} is not a valid value for argument"
                        f" {arg_name!r}, valid values are {allowed_values}"
                    )
            return func(self, *args, **kwargs)

        return cast("_F", wrapper)

    return decorator


def list_instruments(
    suppress: bool = False, backend: Literal["@ivi", "@py", ""] = ""
) -> dict:
    """Scan network for instruments and extract their ID and names.

    If your device does not appear:
        - On the instrument front panel navigate to IO/LAN
          Check the IP address is valid/as expected.
          If not, reset the LAN interface.
        - To check it's available try ping the device in command line.
          (e.g. >ping 172.18.40.127)
        - If it still does not appear use:
          Keysight IO Libraries Suite > Add Instrument > Enter Address
          and put in the address manually.

    After performing this, the device should appear on your PC and any other device.
    If none of these are the case, raise an issue.

    Args:
        suppress: Suppress the printing of each resource (default: False).
        backend: Choose backend for pyvisa to use (default: '@ivi').

    Returns:
        dictionary of resources with ip addresses and names

    """
    rm = pyvisa.ResourceManager(visa_library=backend)
    resources: tuple = rm.list_resources(query="?*::?*")
    resource_names = {}
    for resource in resources:
        try:
            resource_names[resource] = {"address": resource.split("::")[1]}
        except Exception:
            resource_names[resource] = {"address": resource}
        try:
            inst = rm.open_resource(resource)
            if not isinstance(inst, MessageBasedResource):
                raise TypeError(
                    f"Expected MessageBasedResource, but got {inst.__class__.__name__}"
                )
            resource_names[resource]["response"] = inst.query("*IDN?")
            try:
                # Expected string format:
                # 'Rohde&Schwarz,SMCV100B,1432.7000K02/101359,5.00.122.24  \n'
                # Instrument name in position [1]: SMCV100B
                name = resource_names[resource]["response"].split(",")[1]
            except Exception:
                name = ""
            resource_names[resource]["name"] = name
            if not suppress:
                print(f"Resource {resource} - {resource_names[resource]}")
            inst.close()
        except Exception as E:
            print(f"Failed to check resource @ {resource} ({E})")
    return resource_names


def list_methods(obj: object) -> list[str]:
    """List methods in class, excluding built-ins.

    Args:
        obj: Class to get methods for.

    Returns:
        List of methods

    """
    return [
        name
        for name in dir(obj)
        if (
            (
                inspect.ismethod(getattr(obj, name))
                or inspect.isfunction(getattr(obj, name))
            )
            and (
                "not applicable"
                not in ((inspect.getdoc(getattr(obj, name)) or "").lower())
            )
            and not name.startswith("_")
        )
    ]


def find_all_methods(
    package_name: str, package: ModuleType | None = None
) -> Generator[tuple[type, Callable], None, None]:
    """Find all class method in a package."""
    if package is None:
        package = importlib.import_module(package_name)

    for _, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__, package_name + "."
    ):
        full_module_name = module_name

        module = importlib.import_module(full_module_name)

        for _, cls in getmembers(module, isclass):
            # Get all functions (methods) within the class
            for _, method in getmembers(cls, isfunction):
                yield cls, method

            # If it's a sub-package, recurse into it
            if is_pkg:
                yield from find_all_methods(full_module_name, module)
