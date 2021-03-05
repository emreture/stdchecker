"""Functions for fetching standard method data from the IEC website and checking if actual standard methods are
up to date.
"""
import logging
import requests
from collections.abc import Iterable
from bs4 import BeautifulSoup

IEC_SEARCH_URL = "https://webstore.iec.ch/searchkey&key={0}&start=1&MAX=50&FUZZY=0"
log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler()) is not necessary. Parent's handler is already NullHandler.


def search_iec(query_item, session) -> list:
    """
    Gets query results from the IEC search engine.

    :param query_item: Designation or number of the standard method to be searched.
    :param session: A :ref:`Session <requests.Session>` object.
    :return: A list of dicts containing search results.
    """
    found_list = list()
    query_item = str(query_item)
    url = IEC_SEARCH_URL.format(query_item)
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        log.exception("Request exception has occurred.")
        return [{'query': query_item, 'error': "Connection error", 'no': None, 'rev': None, 'desc': None,
                 'body': "iec", 'url': None}]
    html = response.text
    if "No valid publication found." in html:
        log.warning(f"No results found for '{query_item}'.")
        return [{'query': query_item, 'error': "Not found", 'no': None, 'rev': None, 'desc': None,
                 'body': "iec", 'url': None}]
    soup = BeautifulSoup(html, "html.parser")
    try:
        search_result_items = soup.find("ul", {'class': "search-results"}).find_all("li", recursive=False)
        log.debug(f"Found {len(search_result_items)=}.")
        for item in search_result_items:
            found = False
            for c, content in enumerate(item.contents):
                if content.name == "a" and content.get("href", "") == "#":
                    continue
                if content.name == "a" and query_item not in content.string:
                    # std_name = content.string
                    # std_name_split = std_name.split(":")
                    # std_number = std_name_split[0]
                    # std_rev = ":".join(std_name_split[1:]).strip()
                    # std_url = content.get("href")
                    # if std_url:
                    #     std_url = f"https://webstore.iec.ch{std_url}"
                    # found = True
                    pass
                if content.name == "a" and query_item in content.string:
                    std_name = content.string
                    std_name_split = std_name.split(":")
                    std_number = std_name_split[0]
                    # std_rev = std_name_split[1].strip()
                    std_rev = ":".join(std_name_split[1:]).strip()
                    std_url = content.get("href")
                    if std_url:
                        std_url = f"https://webstore.iec.ch{std_url}"
                    found = True
                if content.name == "br" and found:
                    std_desc = item.contents[c + 1].strip()
                    found_list.append(
                        {'query': query_item, 'error': None, 'no': std_number, 'rev': std_rev, 'desc': std_desc,
                         'body': "iec", 'url': std_url})
    except (AttributeError, IndexError):
        log.exception("An exception has occurred while parsing HTML data. IEC search page content may have changed.")
        return [
            {'query': query_item, 'error': "Data parsing error", 'no': None, 'rev': None, 'desc': None, 'body': "iec",
             'url': None}]
    return found_list


def fetch_iec(query_list):
    """
    Fetches data of the latest revision of standard methods from the IEC search engine.

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
            if not query_upper.startswith("IEC "):
                query_upper = "IEC " + query_upper
            found_list = search_iec(query, session)
            for found_item in found_list:
                if found_item['error'] is None:
                    if query_upper == found_item['no']:
                        yield found_item
                else:
                    yield found_item
    return


def check_iec(fetched: Iterable, actual: list, id_from_actual=False):
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of the IEC search engine's result.
    :param actual: A list of dicts containing actual revision data. Dict should include at least 'no' and 'rev' keys
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
        if fetched_item['error'] is None:
            fetched_no = fetched_item['no']
            actual_item = next((i for i in actual if i['no'] == fetched_no), None)
            if actual_item:
                fetched_rev = fetched_item['rev']
                actual_rev = actual_item['rev']
                actual_rev2 = actual_rev
                if " RLV" in fetched_rev:
                    fetched_rev = fetched_rev.replace(" RLV", "")
                if ":" in fetched_rev:
                    fetched_rev = fetched_rev.split(":")[-1]
                    if " CSV" in fetched_rev:
                        fetched_rev = fetched_rev.replace(" CSV", "")
                if " RLV" in actual_rev:
                    actual_rev2 = actual_rev.replace(" RLV", "")
                if ":" in actual_rev2:
                    actual_rev2 = actual_rev2.split(":")[-1]
                    if " CSV" in actual_rev2:
                        actual_rev2 = actual_rev2.replace(" CSV", "")
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


def check_iec_as_list(fetched: Iterable, actual: list, id_from_actual=False) -> list:
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison and an 'error' key to indicate the status of the IEC search engine's result.
    :param actual: A list of dicts containing actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A list of  dicts containing comparison data. The dict includes all items and keys from
        the fetched dict, 'rev' key from the actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    return [i for i in check_iec(fetched, actual, id_from_actual=id_from_actual)]
