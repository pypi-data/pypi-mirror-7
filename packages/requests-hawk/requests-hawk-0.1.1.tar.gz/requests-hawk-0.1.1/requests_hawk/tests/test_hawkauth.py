from requests_hawk import HawkAuth
import unittest


class TestHawkAuth(unittest.TestCase):

    def test_hawkauth_errors_when_credentials_and_hawk_session_passed(self):
        self.assertRaises(AttributeError, HawkAuth,
                          credentials={}, hawk_session="test")

    def test_hawkauth_errors_when_no_auth_is_set(self):
        self.assertRaises(AttributeError, HawkAuth)

    def test_key_non_hex_values_throws(self):
        self.assertRaises(TypeError, HawkAuth, hawk_session="test")

    def test_credentials_are_derived_from_session(self):
        auth = HawkAuth(hawk_session="hello".encode("hex"))
        self.assertDictEqual(auth.credentials, {
            'id': '15064c77e946608226a9c2d8da61ac5e0e85f325334965c68a3f47e8091'
                  'f8412',
            'key': 'cb3829c6d6fe3f58609d58f09818295dfbdf45803ec50b8d66c4132f7a'
                   'd14aa0',
            'algorithm': 'sha256'
        })

    def test_server_url_is_parsed(self):
        auth = HawkAuth(hawk_session="hello".encode("hex"),
                        server_url="http://localhost:5000")
        self.assertEquals(auth.host, "localhost:5000")
