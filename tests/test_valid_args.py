"""Validate the allowed values in the docstrings of functions."""

import logging
import re
from collections.abc import Callable, Sequence
from typing import Any, cast

from inspy.utils import find_all_methods

logger = logging.getLogger("test_valid_args")


def validate_method(cls: type, func: Callable) -> int:
    docstring = func.__doc__
    errors = 0

    if not hasattr(func, "_allowed_values") or not docstring:
        return errors

    allowed_values = cast("dict[str, Sequence[str | int] | str]", func._allowed_values)
    for arg_name, rule in allowed_values.items():
        if isinstance(rule, str):
            rule = getattr(cls, rule)

        for line in docstring.splitlines():
            match = re.match(
                (
                    rf"(\s+{arg_name})"  # Match the arg name
                    r"(?:|\s|\()"  # Positive lookahead to check it's followed by
                    # ':', '(' or a whitespace (without consuming it)
                    r"([^:]*)"  # Group for the type
                    r":.*"  # Must have a colon
                ),
                line,
            )
            if not match:
                continue

            pre = match.group(1).strip()
            got_type = match.group(2).strip()

            expected_type = "(" + " | ".join(repr(v) for v in rule) + ")"
            if got_type != expected_type:
                func_name = cast("Any", func).__name__
                logger.error(
                    f"{cls.__name__}.{func_name} argument docstring should include "
                    f'"{pre} {expected_type}:" (got {got_type!r})'
                )
                errors += 1
            break

    return errors


def test_validate_all_functions(package_name: str = "inspy.instrument") -> None:
    """Validate all functions that have the @validate_allowed_values decorator."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)8s] %(message)s",
    )
    errors = 0
    for cls, method in find_all_methods(package_name):
        errors += validate_method(cls, method)
    assert errors == 0, f"Found {errors} errors"
    print("All docstrings are valid!")


if __name__ == "__main__":
    test_validate_all_functions()
