#Test the loading of users from the config file:

import unittest
import configparser
from user_handlers import SmtpHandler, ImapHandler, MailUser
from main import LocalSmtpHandler

class TestLocalSmtpHandler(unittest.TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('config_sample.ini')
        self.local_handler = LocalSmtpHandler()
        self.local_handler.load_users(self.config)

    def test_load_users(self):
        self.assertEqual(len(self.local_handler.mail_users), 1)
        self.assertIsInstance(self.local_handler.mail_users['example.com@example.com'], MailUser)


if __name__ == '__main__':
    unittest.main()