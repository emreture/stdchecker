import time
import logging
import json
from stdchecker import *

# Standard methods owned as of Dec 31, 2020

astm_list = [
    # chemistry lab
    "D92", "D93", "D97", "D117", "D445", "D446", "D611", "D664", "D923", "D924", "D971", "D1169", "D1500", "D1524",
    "D1533", "D1816", "D2112", "D2144", "D2270", "D2472", "D2668", "D2685", "D3455", "D3487", "D3612", "D4052",
    "D4059", "D4243", "D4768", "D5837", "D5950", "D6871", "D7150"
]

iec_list = [
    # chemistry lab
    60156, 60247, 60296, 60422, 60599, 60666, 60814, 61099, 61198, "62021-1", "62697-1", 62961,
    # transformer test lab
    "60076-1", "60076-2", "60076-3", "60076-6", "60076-8", "60076-10", "60076-10-1", "60076-11", "60076-18", 60270,
    # mv switchgear lab
    "62271-1", "62271-100", "62271-200"
]

ieee_list = [
    # chemistry lab
    "C57.104", "C57.106", "C57.147",
    # transformer test lab
    "C57.12.90", "C57.152", "C57.161", "C57.21"
]

tse_list = [
    # chemistry lab
    "TS EN IEC 61125", "TS EN ISO 3016", "TS EN ISO 3104", "TS 1615 ISO 2977", "TS 1713 ISO 2049", "TS EN ISO 2592",
    "TS EN ISO 2719", "TS ISO 2909", "TS ISO 3105", "TS 3989 EN 60156", "TS EN ISO 12185", "TS EN 14210", "TS EN 60247",
    "TS EN IEC 60296", "TS EN IEC 60376", "TS EN 60422", "TS EN 60450", "TS EN 60475", "TS EN 60567", "TS EN 60599",
    "TS EN 60666", "TS EN 60814", "TS EN 61039", "TS EN 61181", "TS EN 61198", "TS EN 61203", "TS EN 61619",
    "TS EN 62021-1", "TS EN 62021-3", "TS EN 62770",
    # transformer test lab
    "TS EN ISO 2178", "TS EN ISO 2808", "TS 2051 EN 60270", "TS 3033 EN 60529", "TS EN 50588-1", "TS EN 50464-4",
    "TS EN 60060-1", "TS EN 60060-2", "TS EN 60076-1", "TS EN 60076-2", "TS EN 60076-3", "TS EN 60076-4",
    "TS EN 60076-6", "TS EN 60076-10", "TS EN 60076-11", "TS EN IEC 60076-1", "TS EN 60076-18", "TS EN 60076-19",
    "TS EN 62271-1", "TS 10902 EN 60076-3",
    # mv switchgear lab
    "TS EN 62271-100", "TS EN 62271-200",
    # quality manager
    "TS EN ISO/IEC 17025", "TS EN ISO/IEC 17043", "TS 5822-1 ISO 5725-1", "TS 5822-2 ISO 5725-2",
    "TS 5822-3 ISO 5725-3", "TS 5822-4 ISO 5725-4", "TS 5822-5 ISO 5725-5", "TS 5822-6 ISO 5725-6"
]

log = logging.getLogger(__name__)


def fetch_std(func, std_list, filename=None):
    print(f"Running {func.__name__}...")
    start = time.perf_counter()
    fetch_list = func(std_list)
    stop = time.perf_counter()
    print(f"Completed in {round(stop - start, 3)} seconds.")
    if fetch_list and filename:
        with open("data/" + filename, "w", encoding="utf-8") as f:
            json.dump(fetch_list, f, indent=2)


def add_id_to_actual(body):
    with open("data/" + body + "_actual.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for c, item in enumerate(data):
        if item.get("id") is None:
            item['id'] = c
    with open("data/" + body + "_actual.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    fetch_std(fetch_astm, astm_list, "astm_fetched.json")
    fetch_std(fetch_ieee, ieee_list, "ieee_fetched.json")
    fetch_std(fetch_tse, tse_list, "tse_fetched.json")
    fetch_std(fetch_iec, iec_list, "iec_fetched.json")
    add_id_to_actual("astm")
    add_id_to_actual("iec")
    add_id_to_actual("tse")
    add_id_to_actual("ieee")


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    main()
