"""Functions for fetching standard method data from the TSE search engine and checking if actual standard methods are
up to date.
"""
import logging
import requests
from datetime import date
from collections.abc import Iterable
from bs4 import BeautifulSoup

TSE_SEARCH_URL = "https://intweb.tse.org.tr/Standard/Standard/StandardAra.aspx"
log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler()) is not necessary. Parent's handler is already NullHandler.


def search_tse(query_item, session) -> list:
    """
    Gets query results of the TSE search engine.

    :param query_item: Designation or number of the standard method to be searched.
    :param session: A :ref:`Session <requests.Session>` object.
    :return: A list of dicts containing search results.
    """
    found_list = list()
    query_item = str(query_item)
    data = {
        "__EVENTTARGET": "ctl00$cph1$lnkAra",
        "__EVENTARGUMENT": "",
        "ctl00$cph1$txtTsNo": query_item,
        # "ctl00$cph1$StdAramaTip": "rdEsit" not working!
    }
    url = TSE_SEARCH_URL
    try:
        response = session.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        log.exception("Request exception has occurred.")
        return [{'query': query_item, 'error': "Connection error", 'no': None, 'rev': None, 'desc': None,
                 'body': "tse", 'url': None}]
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    try:
        search_result_items = soup.find_all("tr", {'class': ["grvRowStyle", "grvAlternatingRowStyle"]})
        log.debug(f"Found {len(search_result_items)=}.")
        for item in search_result_items:
            td = item.find_all("td")
            std_number = ""
            for span_item in td[2].find_all("span"):
                if span_item.get("id", "").startswith("cph1_grvStandard_lblTsNo"):
                    std_number = span_item.text
                if span_item.get("id", "").startswith("cph1_grvStandard_lblBaslik"):
                    std_desc = span_item.contents[1].strip().replace("\r\n", " ")
            if std_number == "":
                continue
            std_rev = td[3].string
            std_url = TSE_SEARCH_URL
            if query_item != std_number:
                std_number_split = std_number.split(" ")[0].split(":")[0].split("/")[0]
                if query_item != std_number_split:
                    continue
            if "İptal Standard" in std_number:
                continue
            found_list.append(
                {'query': query_item, 'error': None, 'no': std_number, 'rev': std_rev, 'desc': std_desc,
                 'body': "tse", 'url': std_url})
    except (AttributeError, IndexError):
        log.exception("An exception has occurred while parsing HTML data. TSE search page content may have changed.")
        return [{'query': query_item, 'error': "Data parsing error", 'no': None, 'rev': None, 'desc': None,
                 'body': "tse", 'url': None}]
    if found_list:
        return found_list
    else:
        return [{'query': query_item, 'error': "Not found", 'no': None, 'rev': None, 'desc': None,
                 'body': "tse", 'url': None}]


def fetch_tse(query_list):
    """
    Fetches data of the latest revision of standard methods from the TSE search engine.

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
            found_list = search_tse(query, session)
            for found_item in found_list:
                if found_item['error'] is None:
                    if "İptal Standard" not in found_item['no']:
                        yield found_item
                else:
                    yield found_item
    return


def check_tse(fetched: Iterable, actual: list, id_from_actual=False):
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of the TSE search engine's result.
    :param actual: A list of dicts containing actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A generator that yields dicts containing comparison data. Includes all items and keys from
        the fetched dict, 'rev' key from the actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    if not isinstance(fetched, Iterable):
        raise TypeError("'fetched' argument must be an iterable of dicts.")
    if not isinstance(actual, (list, tuple)):
        raise TypeError("'actual' argument must be a list or a tuple of dicts.")
    for fetched_item in fetched:
        checked_item = dict(fetched_item)
        if fetched_item['error'] is None:
            expected_no = fetched_item['no']
            actual_item = next((i for i in actual if i['no'] == expected_no), None)
            if actual_item:
                fetched_rev = fetched_item['rev']
                _ = fetched_rev.split(".")
                fetched_rev_date = date(int(_[2]), int(_[1]), int(_[0]))
                actual_rev = actual_item['rev']
                _ = actual_rev.split(".")
                actual_rev_date = date(int(_[2]), int(_[1]), int(_[0]))
                if fetched_rev_date == actual_rev_date:
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


def check_tse_as_list(fetched: Iterable, actual: list, id_from_actual=False) -> list:
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing latest the revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of the TSE search engine's result.
    :param actual: A list of dicts containing actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A list of dicts containing comparison data. The dict includes all items and keys from
        the fetched dict, 'rev' key from actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    return [i for i in check_tse(fetched, actual, id_from_actual=id_from_actual)]
