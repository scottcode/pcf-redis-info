import unittest
import json

from app_server import app


def response_to_json(response):
    """Convert Flask Response instance to a dict its the JSON-encoded data

    :param response: flask.wrappers.Response
    :return: dict
    """
    # ensure str (and not bytes in Python 3)
    data_str = response.data.decode()
    return json.loads(data_str)



class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_slowlog_len_handler(self):
        response = self.app.get('/redis_slowlog_len')
        self.assertEqual(response.status_code, 200, 'Error in request for slowlog_len')
        data_dict = response_to_json(response)
        slowlog_len = data_dict.get('slowlog_len')
        self.assertIsNotNone(slowlog_len, 'Did not receive slowlog_len key')
        self.assertGreaterEqual(
            slowlog_len, 0,
            "slowlog length should be >=0. It is {}".format(slowlog_len)
        )

    def test_slowlog_get_noarg(self):
        response = self.app.get('/redis_slowlog_get')
        self.assertEqual(response.status_code, 200, 'Error in request for slowlog_get')
        data_dict = response_to_json(response)
        slowlog_list = data_dict.get('slowlog_list')
        self.assertIsNotNone(slowlog_list, 'Did not receive slowlog_list key')
        self.assertIsInstance(
            slowlog_list, list,
            "slowlog_get should give a list. Got {}".format(type(slowlog_list))
        )

    def test_slowlog_get_valid_arg(self):
        n = 20
        response = self.app.get('/redis_slowlog_get?n={}'.format(n))
        self.assertEqual(response.status_code, 200, 'Error in request for slowlog_get with valid arg')
        data_dict = response_to_json(response)
        slowlog_list = data_dict.get('slowlog_list')
        self.assertIsNotNone(slowlog_list, 'Did not receive slowlog_list key')
        self.assertIsInstance(
            slowlog_list, list,
            "slowlog_get should give a list. Got {}".format(type(slowlog_list))
        )
        self.assertLessEqual(
            len(slowlog_list), n,
            "Expected slowlog with max {}, got length={}".format(n, len(slowlog_list))
        )

    def test_slowlog_get_invalid_arg(self):
        response = self.app.get('/redis_slowlog_get?n=foo')
        self.assertEqual(response.status_code, 200, 'Error in request for slowlog_get with invalid arg')
        data_dict = response_to_json(response)
        slowlog_list = data_dict.get('slowlog_list')
        self.assertIsNotNone(slowlog_list, 'Did not receive slowlog_list key')
        self.assertIsInstance(
            slowlog_list, list,
            "slowlog_get should give a list. Got {}".format(type(slowlog_list))
        )


if __name__ == '__main__':
    unittest.main()
