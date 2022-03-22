import logging
from stdchecker.astm import fetch_astm, check_astm, check_astm_as_list
from stdchecker.iec import fetch_iec, check_iec, check_iec_as_list
from stdchecker.tse import fetch_tse, check_tse, check_tse_as_list
from stdchecker.ieee import fetch_ieee, check_ieee, check_ieee_as_list

__title__ = "stdchecker"
__version__ = "0.1.3"
__author__ = "Metin Emre TÜRE"
__email__ = "emreture@gmail.com"
__license__ = "MIT"
__status__ = "development"

__all__ = [
    "fetch_astm",
    "check_astm",
    "check_astm_as_list",
    "fetch_iec",
    "check_iec",
    "check_iec_as_list",
    "fetch_tse",
    "check_tse",
    "check_tse_as_list",
    "fetch_ieee",
    "check_ieee",
    "check_ieee_as_list"
]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
