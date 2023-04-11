import configparser
import smtplib
import imaplib
from email.message import Message
from email.contentmanager import ContentManager
from time import time


class SmtpHandler:
    """Параметры для авторизации по smtp"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        use_ssl=False,
        start_tls=False,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._start_tls = start_tls

    @staticmethod
    def load_smtp(config: configparser.ConfigParser, email: str):
        # TODO checking
        key_value = f"smtp_{email}"

        host = config.get(key_value, "host")
        port = config.getint(key_value, "port")
        # user - not need ?
        password = config.get(key_value, "password")
        use_ssl = config.getboolean(key_value, "use_ssl")
        start_ssl = config.getboolean(key_value, "start_tls")

        return SmtpHandler(host, port, email, password, use_ssl, start_ssl)

    def implement_email(self, rcpt_tos, original_content: bytes):
        # TODO all exception handler!!!
        # TODO test session place in self context
        if self._use_ssl:
            session = smtplib.SMTP_SSL(self._host, self._port)
        else:
            session = smtplib.SMTP(self._host, self._port)

        if self._start_tls:
            session.starttls()
            session.ehlo()

        if self._user and self._password:
            session.login(self._user, self._password)
        try:
            session.sendmail(self._user, rcpt_tos, original_content)
        except Exception as var_error:
            Exception(var_error)
        finally:
            # need only quit?
            session.quit()


class ImapHandler:
    """Параметры для авторизации Imap"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        use_ssl=False,
        folder="Sent",
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        print(use_ssl)
        self._use_ssl = use_ssl
        self._folder = folder

    @staticmethod
    def load_imap(config: configparser.ConfigParser, email: str):
        key_value = f"imap_{email}"

        host = config.get(key_value, "host")
        port = config.getint(key_value, "port")
        # user - not need ?
        password = config.get(key_value, "password")
        use_ssl = config.getboolean(key_value, "use_ssl")
        folder = config.get(key_value, "folder").strip()

        return ImapHandler(host, port, email, password, use_ssl, folder)

    def implement_email(self, rcpt_tos, original_content: bytes):
        # TODO all exception handler!!!
        # TODO test session place in self context
        if self._use_ssl:
            session = imaplib.IMAP4_SSL(self._host, self._port)
        else:
            session = imaplib.IMAP4(self._host, self._port)
        print(self._user, self._password)
        session.login(self._user, self._password)

        print(session.list())
        value = original_content
        print(value)
        # TODO folder to config
        res = session.append(self._folder, "", imaplib.Time2Internaldate(time()), value)
        print("res", res)
        try:
            pass
        except Exception as var_error:
            print(var_error)
        finally:
            session.logout()


class MailUser:
    def __init__(
        self, login: str, smtp_handler: SmtpHandler, imap_handler: ImapHandler
    ):
        self.login = login
        self.smtp_handler = smtp_handler
        self.imap_handler = imap_handler

    def __eq__(self, value):
        return isinstance(value, self.__class__) and self.login == value.login

    def __hash__(self):
        return hash(self.login)
