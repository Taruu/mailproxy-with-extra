import unittest
import configparser
from user_handlers import SmtpHandler, ImapHandler, MailUser
from main import LocalSmtpHandler

class TestLocalSmtpHandler(unittest.TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('unittest_config.ini')
        self.local_handler = LocalSmtpHandler()
        self.local_handler.load_users(self.config)

    def test_handle_data(self):
        server = None
        session = None
        envelope = {
            'mail_from': 'example.com@example.com',
            'rcpt_tos': ['user2@example.com', 'user3@example.com'],
            'original_content': 'Test message'
        }
        response = self.local_handler.handle_data(server, session, envelope)
        self.assertEqual(response, '250 OK')
        self.assertEqual(self.local_handler.mail_users['user2@example.com'].imap_handler.inbox[0]['content'], 'Test message')
        self.assertEqual(self.local_handler.mail_users['user3@example.com'].imap_handler.inbox[0]['content'], 'Test message')

if __name__ == '__main__':
    unittest.main()