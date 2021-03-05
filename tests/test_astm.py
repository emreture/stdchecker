import os
import json
import unittest
from unittest.mock import patch
from requests import Session, ConnectionError, HTTPError
from stdchecker.astm import fetch_astm, check_astm, check_astm_as_list

MODULE_PATH = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    @patch.object(Session, "get")
    def test_fetch(self, mock_get):
        with open(os.path.join(MODULE_PATH, "webdata/D92.html"), "r", encoding="utf-8") as f:
            mock_get.return_value.text = f.read()
        std_list = list(fetch_astm("D92"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("D92", std['query'])
        self.assertEqual(None, std['error'])
        self.assertEqual("ASTM D92", std['no'])
        self.assertEqual("18", std['rev'])
        self.assertEqual("Standard Test Method for Flash and Fire Points by Cleveland Open Cup Tester", std['desc'])
        self.assertEqual("astm", std['body'])
        self.assertEqual("https://www.astm.org/Standards/D92.htm", std['url'])

    @patch.object(Session, "get")
    def test_fetch_not_found_error(self, mock_get):
        mock_get.side_effect = HTTPError("http error side effect")
        std_list = list(fetch_astm("BAD D92"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("BAD D92", std['query'])
        self.assertEqual("Not found", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("astm", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "get")
    def test_fetch_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError("connection error side effect")
        std_list = list(fetch_astm("D92"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("D92", std['query'])
        self.assertEqual("Connection error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("astm", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "get")
    def test_fetch_data_parsing_error(self, mock_get):
        mock_get.return_value.text = "Bad webpage"
        std_list = list(fetch_astm("D92"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("D92", std['query'])
        self.assertEqual("Data parsing error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("astm", std['body'])
        self.assertEqual(None, std['url'])

    def test_fetch_type_error(self):
        with self.assertRaises(TypeError):
            list(fetch_astm(92))

    def test_check(self):
        with open(os.path.join(MODULE_PATH, "data/astm_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/astm_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        # actual_check = json.loads(json.dumps([i for i in check_astm(fetched, actual)]))
        actual_check = [i for i in check_astm(fetched, actual)]
        actual_check_with_id = [i for i in check_astm(fetched, actual, id_from_actual=True)]
        with open(os.path.join(MODULE_PATH, "data/astm_check.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_with_id)
        actual_check_as_list = check_astm_as_list(fetched, actual)
        actual_check_as_list_with_id = check_astm_as_list(fetched, actual, id_from_actual=True)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_with_id)

    def test_check_with_id(self):
        with open(os.path.join(MODULE_PATH, "data/astm_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/astm_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        actual_check = [i for i in check_astm(fetched, actual, id_from_actual=True)]
        actual_check_without_id = [i for i in check_astm(fetched, actual)]
        with open(os.path.join(MODULE_PATH, "data/astm_check_with_id.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_without_id)
        actual_check_as_list = check_astm_as_list(fetched, actual, id_from_actual=True)
        actual_check_as_list_without_id = check_astm_as_list(fetched, actual)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_without_id)


if __name__ == '__main__':
    unittest.main()
