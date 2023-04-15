import configparser
import smtplib
import imaplib
from time import time
import logging
from typing import List


class SmtpHandler:
    """Параметры для авторизации по smtp"""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        use_ssl: bool = False,
        start_tls: bool = False,
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._start_tls = start_tls

    @staticmethod
    def load_smtp(config: configparser.ConfigParser, email: str):
        key_value = f"smtp_{email}"
        try:
            host = config.get(key_value, "host")
            port = config.getint(key_value, "port")
            # user - not need ?
            password = config.get(key_value, "password")
            use_ssl = config.getboolean(key_value, "use_ssl")
            start_tls = config.getboolean(key_value, "start_tls")
        except ValueError as e:
            logging.error(f"Invalid value found for a variable {e}.")
            return None
        except configparser.NoOptionError as e:
            logging.error(f"No option {e.option} found in section {e.section}.")
            return None
        except configparser.NoSectionError as e:
            logging.error(f"Section {e.section} not found.")
            return None
        except configparser.ParsingError:
            logging.error("Error while parsing the configuration file.")
            return None

        return SmtpHandler(host, port, email, password, use_ssl, start_tls)

    def send_email(self, rcpt_tos: List[str], original_content: bytes):
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

        refused_recipients = {}
        try:
            # TODO check before call
            refused_recipients = session.sendmail(
                self._user, rcpt_tos, original_content
            )
        except smtplib.SMTPRecipientsRefused:
            logging.error(f"Recipients refused: {' '.join(refused_recipients.keys())}")
            return f'553 Recipients refused {"".join(refused_recipients.keys())}'

        except smtplib.SMTPResponseException as e:
            logging.error(f"SMTP response exception: {e.smtp_code} {e.smtp_error}")
            return f"{e.smtp_code} {e.smtp_error}"

        except Exception as e:
            logging.error(f"Exception while implementing email using SMTP: {str(e)}")

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
        use_ssl: bool = False,
        folder="Sent",
    ):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._folder = folder

    @staticmethod
    def load_imap(config: configparser.ConfigParser, email: str):
        key_value = f"imap_{email}"
        try:
            host = config.get(key_value, "host")
            port = config.getint(key_value, "port")
            # user - not need ?
            password = config.get(key_value, "password")
            use_ssl = config.getboolean(key_value, "use_ssl")
            folder = config.get(key_value, "folder").strip()
        except ValueError as e:
            logging.error(f"Invalid value found for a variable {e}.")
            return None
        except configparser.NoOptionError as e:
            logging.error(f"No option {e.option} found in section {e.section}.")
            return None
        except configparser.NoSectionError as e:
            logging.error(f"Section {e.section} not found.")
            return None
        except configparser.ParsingError:
            logging.error("Error while parsing the configuration file.")
            return None

        return ImapHandler(host, port, email, password, use_ssl, folder)

    def store_email(self, rcpt_tos: List[str], original_content: bytes):
        # TODO all exception handler!!!
        # TODO test session place in self context
        if self._use_ssl:
            session = imaplib.IMAP4_SSL(self._host, self._port)
        else:
            session = imaplib.IMAP4(self._host, self._port)

        session.login(self._user, self._password)

        value = original_content
        # TODO folder to config
        res = session.append(self._folder, "", imaplib.Time2Internaldate(time()), value)
        try:
            pass
        except Exception as var_error:
            logging.error(var_error)
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
