import os
import json
import unittest
from unittest.mock import patch
from requests import Session, ConnectionError
from stdchecker.ieee import fetch_ieee, check_ieee, check_ieee_as_list

MODULE_PATH = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    @patch.object(Session, "get")
    def test_fetch(self, mock_get):
        with open(os.path.join(MODULE_PATH, "webdata/ieee_search.json"), "r", encoding="utf-8") as f:
            mock_get.return_value.json = lambda: json.load(f)
            std_list = list(fetch_ieee("C57.104"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("C57.104", std['query'])
        self.assertEqual(None, std['error'])
        self.assertEqual("IEEE C57.104", std['no'])
        self.assertEqual("2019", std['rev'])
        self.assertEqual("IEEE Guide for the Interpretation of Gases Generated in Mineral Oil-Immersed Transformers",
                         std['desc'])
        self.assertEqual("ieee", std['body'])
        self.assertEqual("https://standards.ieee.org/content/ieee-standards/en/standard/C57_104-2019.html", std['url'])

    @patch.object(Session, "get")
    def test_fetch_not_found_error(self, mock_get):
        with open(os.path.join(MODULE_PATH, "webdata/ieee_not_found.json"), "r", encoding="utf-8") as f:
            mock_get.return_value.json = lambda: json.load(f)
            std_list = list(fetch_ieee("BAD C57.104"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("BAD C57.104", std['query'])
        self.assertEqual("Not found", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("ieee", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "get")
    def test_fetch_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError("connection error side effect")
        std_list = list(fetch_ieee("C57.104"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("C57.104", std['query'])
        self.assertEqual("Connection error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("ieee", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "get")
    def test_fetch_data_parsing_error(self, mock_get):
        mock_get.return_value.json = lambda: json.loads("{}")
        std_list = list(fetch_ieee("C57.104"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("C57.104", std['query'])
        self.assertEqual("Data parsing error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("ieee", std['body'])
        self.assertEqual(None, std['url'])

    def test_fetch_type_error(self):
        with self.assertRaises(TypeError):
            list(fetch_ieee(57))

    def test_check(self):
        with open(os.path.join(MODULE_PATH, "data/ieee_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/ieee_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        actual_check = [i for i in check_ieee(fetched, actual)]
        actual_check_with_id = [i for i in check_ieee(fetched, actual, id_from_actual=True)]
        with open(os.path.join(MODULE_PATH, "data/ieee_check.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_with_id)
        actual_check_as_list = check_ieee_as_list(fetched, actual)
        actual_check_as_list_with_id = check_ieee_as_list(fetched, actual, id_from_actual=True)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_with_id)

    def test_check_with_id(self):
        with open(os.path.join(MODULE_PATH, "data/ieee_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/ieee_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        actual_check = [i for i in check_ieee(fetched, actual, id_from_actual=True)]
        actual_check_without_id = [i for i in check_ieee(fetched, actual)]
        with open(os.path.join(MODULE_PATH, "data/ieee_check_with_id.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_without_id)
        actual_check_as_list = check_ieee_as_list(fetched, actual, id_from_actual=True)
        actual_check_as_list_without_id = check_ieee_as_list(fetched, actual)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_without_id)


if __name__ == '__main__':
    unittest.main()
