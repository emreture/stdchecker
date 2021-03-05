import os
import json
import unittest
from unittest.mock import patch
from requests import Session, ConnectionError
from stdchecker.tse import fetch_tse, check_tse, check_tse_as_list

MODULE_PATH = os.path.dirname(__file__)


class TestCase(unittest.TestCase):
    @patch.object(Session, "post")
    def test_fetch(self, mock_post):
        with open(os.path.join(MODULE_PATH, "webdata/tse.html"), "r", encoding="utf-8") as f:
            mock_post.return_value.text = f.read()
        std_list = list(fetch_tse("TS EN IEC 60296"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("TS EN IEC 60296", std['query'])
        self.assertEqual(None, std['error'])
        self.assertEqual("TS EN IEC 60296 (İngilizce Metin) (Renkli)", std['no'])
        self.assertEqual("09.11.2020", std['rev'])
        self.assertEqual("Akışkanlar-Elektroteknik uygulamalar için - Elektrikli cihazlar için mineral yalıtım yağları",
                         std['desc'])
        self.assertEqual("tse", std['body'])
        self.assertEqual("https://intweb.tse.org.tr/Standard/Standard/StandardAra.aspx", std['url'])

    @patch.object(Session, "post")
    def test_fetch_not_found_error(self, mock_post):
        with open(os.path.join(MODULE_PATH, "webdata/tse_not_found.html"), "r", encoding="utf-8") as f:
            mock_post.return_value.text = f.read()
        std_list = list(fetch_tse("BAD TS EN IEC 60296"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("BAD TS EN IEC 60296", std['query'])
        self.assertEqual("Not found", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("tse", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "post")
    def test_fetch_connection_error(self, mock_post):
        mock_post.side_effect = ConnectionError("connection error side effect")
        std_list = list(fetch_tse("TS EN IEC 60296"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("TS EN IEC 60296", std['query'])
        self.assertEqual("Connection error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("tse", std['body'])
        self.assertEqual(None, std['url'])

    @patch.object(Session, "post")
    def test_fetch_data_parsing_error(self, mock_post):
        with open(os.path.join(MODULE_PATH, "webdata/tse_data_parse_error.html"), "r", encoding="utf-8") as f:
            mock_post.return_value.text = f.read()
        std_list = list(fetch_tse("TS EN IEC 60296"))
        self.assertEqual(1, len(std_list))
        std = std_list[0]
        self.assertEqual("TS EN IEC 60296", std['query'])
        self.assertEqual("Data parsing error", std['error'])
        self.assertEqual(None, std['no'])
        self.assertEqual(None, std['rev'])
        self.assertEqual(None, std['desc'])
        self.assertEqual("tse", std['body'])
        self.assertEqual(None, std['url'])

    def test_fetch_type_error(self):
        with self.assertRaises(TypeError):
            list(fetch_tse(60296))

    def test_check(self):
        with open(os.path.join(MODULE_PATH, "data/tse_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/tse_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        actual_check = [i for i in check_tse(fetched, actual)]
        actual_check_with_id = [i for i in check_tse(fetched, actual, id_from_actual=True)]
        with open(os.path.join(MODULE_PATH, "data/tse_check.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_with_id)
        actual_check_as_list = check_tse_as_list(fetched, actual)
        actual_check_as_list_with_id = check_tse_as_list(fetched, actual, id_from_actual=True)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_with_id)

    def test_check_with_id(self):
        with open(os.path.join(MODULE_PATH, "data/tse_fetched.json"), "r", encoding="utf-8") as f:
            fetched = json.load(f)
        with open(os.path.join(MODULE_PATH, "data/tse_actual.json"), "r", encoding="utf-8") as f:
            actual = json.load(f)
        actual_check = [i for i in check_tse(fetched, actual, id_from_actual=True)]
        actual_check_without_id = [i for i in check_tse(fetched, actual)]
        with open(os.path.join(MODULE_PATH, "data/tse_check_with_id.json"), "r", encoding="utf-8") as f:
            expected_check = json.load(f)
        self.assertEqual(expected_check, actual_check)
        self.assertNotEqual(expected_check, actual_check_without_id)
        actual_check_as_list = check_tse_as_list(fetched, actual, id_from_actual=True)
        actual_check_as_list_without_id = check_tse_as_list(fetched, actual)
        self.assertEqual(expected_check, actual_check_as_list)
        self.assertNotEqual(expected_check, actual_check_as_list_without_id)


if __name__ == '__main__':
    unittest.main()
