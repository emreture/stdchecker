"""Functions for fetching standard method data from the IEEE search engine and checking if actual standard methods are
up to date.
"""
import logging
import json
import requests
from collections.abc import Iterable
from .constants import USER_AGENT

IEEE_SEARCH_URL = "https://standards.ieee.org/wp-admin/admin-ajax.php"
log = logging.getLogger(__name__)
# log.addHandler(logging.NullHandler()) is not necessary. Parent's handler is already NullHandler.


def search_ieee(query_item, session) -> list:
    """
    Gets query results from the IEEE search engine.

    :param query_item: Designation or number of the standard method to be searched.
    :param session: A :ref:`Session <requests.Session>` object.
    :return: A list of dicts containing search results.
    """
    found_list = list()
    query_item = str(query_item)
    data = {
        'action': "ieee_cloudsearch",
        'q': query_item,
        'type': "|Standard"
    }
    url = IEEE_SEARCH_URL
    try:
        response = session.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        log.exception("Request exception has occurred.")
        return [{'query': query_item, 'error': "Connection error", 'no': None, 'rev': None, 'desc': None,
                 'body': "ieee", 'url': None}]
    try:
        response_json = response.json()
        if response_json["status"] == "ok":
            data = response_json.get("results", None)
            if data:
                for item in data['hits']['hit']:
                    std_name = item['fields']['doc_title_t'][10:]
                    std_name_split = std_name.split("-")
                    start_index = item['fields']['doc_text_t'].find("MAC Address")
                    end_index = item['fields']['doc_text_t'].find("Purchase", start_index)
                    desc_index = item['fields']['doc_text_t'].find(std_name, start_index) + len(std_name)
                    std_desc = item['fields']['doc_text_t'][desc_index + 1:end_index - 1]
                    std_number = std_name_split[0]
                    std_rev = std_name_split[1]
                    std_url = item['fields']['doc_id_l']
                    if std_number.startswith("IEEE " + query_item) or std_number.startswith("P" + query_item):
                        if not std_rev and std_number.startswith("P" + query_item):
                            std_rev = "project"
                        # Append corrigenda to standard's number so that 'no' item can be unique.
                        corrigenda = std_rev.split("/")[-1] if "/" in std_rev else ""
                        corrigenda = corrigenda.split("-")[0] if "-" in corrigenda else corrigenda
                        std_number = std_number + "/" + corrigenda if corrigenda else std_number
                        found_list.append(
                            {'query': query_item, 'error': None, 'no': std_number, 'rev': std_rev, 'desc': std_desc,
                             'body': "ieee", 'url': std_url})
            else:
                log.warning(f"No results found for '{query_item}'.")
                return [{'query': query_item, 'error': "Not found", 'no': None, 'rev': None, 'desc': None,
                         'body': "ieee", 'url': None}]
    except (json.JSONDecodeError, KeyError, IndexError):
        log.exception("An exception has occurred while parsing JSON data. IEEE search page content may have changed.")
        return [{'query': query_item, 'error': "Data parsing error", 'no': None, 'rev': None, 'desc': None,
                 'body': "ieee", 'url': None}]
    # IEEE search engine returns all revisions (latest and older ones). Older revisions will be excluded.
    filtered_found_list = list()
    sorted_list = sorted(found_list, key=lambda k: k['rev'], reverse=True)
    rev_check = None
    dict_check = dict()
    for sorted_item in sorted_list:
        if sorted_item['error'] is not None:
            filtered_found_list.append(sorted_item)
            break
        if sorted_item['rev'] == "project":
            filtered_found_list.append(sorted_item)
            continue
        if rev_check is None:
            rev_check = sorted_item['rev'][:4]
            dict_check = sorted_item
            filtered_found_list.append(sorted_item)
        else:
            if rev_check in sorted_item['rev']:  # and sorted_item != dict_check:
                compare = (sorted_item['no'] == dict_check['no'],
                           sorted_item['rev'] == dict_check['rev'],
                           sorted_item['desc'] == dict_check['desc'])
                if not all(compare):
                    filtered_found_list.append(sorted_item)
    return filtered_found_list


def fetch_ieee(query_list):
    """
    Fetches data of the latest revision of standard methods from the IEEE search engine.

    :param query_list: A string or an iterable object contains query strings. A query string should be designation
        (or number) of a standard method.
    :return: A generator that yields dicts containing data of the latest standard method(s).
    """
    if isinstance(query_list, str):
        query_list = (query_list,)
    if not isinstance(query_list, Iterable):
        raise TypeError(f"Argument must be a string or an iterable object, {query_list.__class__.__name__} given.")
    with requests.Session() as session:
        session.headers.update({'User-Agent': USER_AGENT})
        for query in query_list:
            query = str(query)
            found_list = search_ieee(query, session)
            for found_item in found_list:
                yield found_item
    return


def check_ieee(fetched: Iterable, actual: list, id_from_actual=False):
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison.
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
        fetched_no = fetched_item['no']
        actual_item = next((i for i in actual if i['no'] == fetched_no), None)
        if actual_item:
            fetched_rev = fetched_item['rev']
            actual_rev = actual_item['rev']
            if fetched_rev == actual_rev:
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
    return


def check_ieee_as_list(fetched: Iterable, actual: list, id_from_actual=False) -> list:
    """
    Checks the revision status of actual standard methods.

    :param fetched: An iterable of dicts containing the latest revision data. Dict should include at least 'no' and
        'rev' keys for comparison.
    :param actual: A list of dicts containing actual revision data. Dict should include at least 'no' and 'rev' keys
        for comparison.
    :param id_from_actual: If True, 'id' key from the actual dict will be included in the resulting dict.
    :return: A list of dicts containing comparison data. The dict includes all items and keys from
        the fetched dict, 'rev' key from the actual dict as 'actual' and 'check' key which is the comparison result
        as boolean. Also includes 'id' key from the actual dict if 'id_from_actual' is True.
    """
    return [i for i in check_ieee(fetched, actual, id_from_actual=id_from_actual)]
