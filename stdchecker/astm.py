"""Functions for fetching standard method data from the ASTM website and checking if actual standard methods are
up to date.
"""
import logging
import requests
from collections.abc import Iterable
from bs4 import BeautifulSoup

ASTM_URL = "https://www.astm.org/Standards/{0}.htm"
log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler()) is not necessary since parent's handler is already NullHandler.


def fetch_astm(query_list):
    """
    Fetches data of the latest revision of standard methods from the ASTM website.

    :param query_list: A string or an iterable object contains query strings. A query string should be designation
        (or number) of a standard method.
    :return: A generator that yields dicts containing data of the latest standard method(s).
    """
    if isinstance(query_list, str):
        query_list = (query_list,)
    if not isinstance(query_list, Iterable):
        raise TypeError(f"Argument must be a string or an iterable object, {query_list.__class__.__name__} given.")
    with requests.Session() as session:
        for query in query_list:
            query = str(query)
            query_upper = query.upper()
            if query_upper.startswith("ASTM "):
                query_upper = query_upper.replace("ASTM ", "")
            url = ASTM_URL.format(query_upper)
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
            except requests.HTTPError:
                log.exception("Request exception has occurred.")
                yield {'query': query, 'error': "Not found", 'no': None, 'rev': None, 'desc': None, 'body': "astm",
                       'url': None}
                continue
            except requests.ConnectionError:
                log.exception("Request exception has occurred.")
                yield {'query': query, 'error': "Connection error", 'no': None, 'rev': None, 'desc': None,
                       'body': "astm", 'url': None}
                continue
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            try:
                std_name = soup.find("b", {'class': "sku"}).string.replace('\xa0', ' ')
                std_desc = soup.find("b", {'class': "name"}).text.strip()
                std_name_split = std_name.split("-")
                std_number = std_name_split[0]
                std_rev = std_name_split[1]
            except (AttributeError, IndexError):
                log.exception("An exception has occurred while parsing HTML data. ASTM page content may have changed.")
                yield {'query': query, 'error': "Data parsing error", 'no': None, 'rev': None, 'desc': None,
                       'body': "astm", 'url': None}
                continue
            yield {'query': query, 'error': None, 'no': std_number, 'rev': std_rev, 'desc': std_desc, 'body': "astm",
                   'url': url}
    return


def check_astm(fetched: Iterable, actual: list, id_from_actual=False):
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of fetching.
    :param actual: A list of dicts containing the actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A generator that yields dicts containing comparison data. The dict includes all items and keys from
        the fetched dict, 'rev' key from the actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    if not isinstance(fetched, Iterable):
        raise TypeError("'fetched' argument must be an iterable of dicts.")
    if not isinstance(actual, (list, tuple)):
        raise TypeError("'actual' argument must be a list or a tuple of dicts.")
    for fetched_item in fetched:
        checked_item = dict(fetched_item)
        if fetched_item["error"] is None:
            fetched_no = fetched_item['no']
            actual_item = next((i for i in actual if i['no'] == fetched_no), None)
            if actual_item:
                fetched_rev = fetched_item['rev']
                actual_rev = actual_item['rev']
                if "(" in fetched_rev and ")" in fetched_rev:
                    fetched_rev = fetched_rev[0:fetched_rev.rfind("(")]
                if "(" in actual_rev and ")" in actual_rev:
                    actual_rev2 = actual_rev[0:actual_rev.rfind("(")]
                else:
                    actual_rev2 = actual_rev
                if fetched_rev == actual_rev2:
                    checked_item['check'] = True
                else:
                    checked_item['check'] = False
                checked_item['actual'] = actual_rev
                if id_from_actual:
                    checked_item['id'] = actual_item.get("id")
                yield checked_item
            else:
                checked_item['actual'] = "Yok"
                checked_item['check'] = False
                if id_from_actual:
                    checked_item['id'] = None
                yield checked_item
        else:
            checked_item['actual'] = "Yok"
            checked_item['check'] = False
            if id_from_actual:
                checked_item['id'] = None
            yield checked_item
    return


def check_astm_as_list(fetched: Iterable, actual: list, id_from_actual=False) -> list:
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of fetching.
    :param actual: A list of dicts containing the actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A list of dicts containing comparison data. The dict includes all items and keys from
        the fetched dict, 'rev' key from the actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    return [i for i in check_astm(fetched, actual, id_from_actual=id_from_actual)]
