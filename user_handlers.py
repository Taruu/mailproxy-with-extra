import smtplib
import imaplib
from email.message import Message
from time import time


class SmtpHandler:
    """Параметры для авторизации по smtp"""

    def __init__(self, host: str, port: int,
                 user: str, password: str,
                 use_ssl=False, start_tls=False):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._start_tls = False

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
            pass
        finally:
            # need only quit?
            session.close()
            session.quit()


class ImapHandler:
    """Параметры для авторизации Imap"""

    def __init__(self, host: str, port: int,
                 user: str, password: str,
                 use_ssl=False, ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl

        pass

    def implement_email(self, rcpt_tos, original_content: bytes):

        # TODO all exception handler!!!
        # TODO test session place in self context
        if self._use_ssl:
            session = imaplib.IMAP4_SSL(self._host, self._port)
        else:
            session = imaplib.IMAP4(self._host, self._port)
        session.login(self._user, self._password)

        #look how we get email content
        new_message = Message()
        new_message["From"] = self._user

        try:

        except Exception as var_error:
            pass
        finally:
            # need only quit?
            session.close()
            session.quit()


class MailUser:
    def __init__(self, user: str, password: str,
                 smtp_host: str, smtp_port: int
        smtp_use_ssl =

    ):
    self._user = user
    self._password = password
    pass


def __str__(self):
    return f'Username: {self._user}'
