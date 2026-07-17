import logging
import os

from pytest import FixtureRequest, fixture


@fixture(scope="module")
def address_from_env(request: FixtureRequest) -> str:
    """Get the address specified in an environment variable.

    E.g. if the test file is called test_agilent_34410A.py, the environment variable
    should be called AGILENT_34410A_ADDRESS, and this function will load the VISA
    address specified in that variable.
    """
    name = request.module.__name__.split(".")[-1]
    address = os.getenv((name.removeprefix("test_") + "_address").upper(), "UNSET")

    logger = logging.getLogger(__name__)

    if address != "UNSET":
        logger.info(f"ADDRESS: {name} = {address}")

    return address
