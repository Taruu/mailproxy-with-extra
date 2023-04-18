import configparser
import smtplib
import imaplib
from time import time
import logging
from typing import List


class SmtpHandler:
    """Smtp handler"""

    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            use_ssl: bool = False,
            start_tls: bool = False,
    ):
        """

        @param host:
        @param port:
        @param user:
        @param password:
        @param use_ssl:
        @param start_tls:
        """

        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._start_tls = start_tls

    @staticmethod
    def load_smtp(config: configparser.ConfigParser, email: str):
        """
        Load smtp handler.

        @param config: config data to load
        @param email: email to load
        @return: SmtpHandler class
        """
        key_value = f"smtp_{email}"
        try:

            host = config.get(key_value, "host")
            port = config.getint(key_value, "port")
            # user - not need ?
            password = config.get(key_value, "password")
            use_ssl = config.getboolean(key_value, "use_ssl")
            start_tls = config.getboolean(key_value, "start_tls")
            return SmtpHandler(host, port, email, password, use_ssl, start_tls)

        except ValueError as e:
            logging.error(f"Invalid value found for a variable {e}.")
        except configparser.NoOptionError as e:
            logging.error(f"No option {e.option} found in section {e.section}.")
        except configparser.NoSectionError as e:
            logging.error(f"Section {e.section} not found.")
        except configparser.ParsingError:
            logging.error("Error while parsing the configuration file.")
        return None

    def send_email(self, rcpt_tos: List[str], original_content: bytes):
        """

        @param rcpt_tos: list emails to receive emails.
        @param original_content: letter content
        @return:
        """

        # TODO test session place in self context?
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
            logging.error(
                f"Recipients refused: {' '.join(refused_recipients.keys())}")
            return f'553 Recipients refused {"".join(refused_recipients.keys())}'

        except smtplib.SMTPResponseException as e:
            logging.error(
                f"SMTP response exception: {e.smtp_code} {e.smtp_error}")
            return f"{e.smtp_code} {e.smtp_error}"
        except Exception as e:
            logging.error(
                f"Exception while implementing email using SMTP: {str(e)}")

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
        """

        @param host:
        @param port:
        @param user:
        @param password:
        @param use_ssl:
        @param folder:
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._use_ssl = use_ssl
        self._folder = folder

    @staticmethod
    def load_imap(config: configparser.ConfigParser, email: str):
        """Load imap from config"""
        key_value = f"imap_{email}"
        try:

            host = config.get(key_value, "host")
            port = config.getint(key_value, "port")
            password = config.get(key_value, "password")
            use_ssl = config.getboolean(key_value, "use_ssl")
            folder = config.get(key_value, "folder").strip()
            return ImapHandler(host, port, email, password, use_ssl, folder)

        except ValueError as e:
            logging.error(f"Invalid value found for a variable {e}.")
        except configparser.NoOptionError as e:
            logging.error(f"No option {e.option} found in section {e.section}.")
        except configparser.NoSectionError as e:
            logging.error(f"Section {e.section} not found.")
        except configparser.ParsingError:
            logging.error("Error while parsing the configuration file.")
        except Exception as e:
            logging.error(
                f"Exception while implementing email using IMAP: {str(e)}")
        return None

    def store_email(self, original_content: bytes):

        # TODO test session place in self context?
        if self._use_ssl:
            session = imaplib.IMAP4_SSL(self._host, self._port)
        else:
            session = imaplib.IMAP4(self._host, self._port)

        try:
            session.login(self._user, self._password)
        except Exception as e:
            logging.error(
                f"Exception while login email using IMAP: {str(e)}")

        value = original_content
        try:
            session.append(self._folder, "",
                           imaplib.Time2Internaldate(time()), value)
        except Exception as e:
            logging.error(
                f"Exception while append email using IMAP: {str(e)}")
        finally:
            session.logout()


class MailUser:
    def __init__(
            self, login: str, smtp_handler: SmtpHandler,
            imap_handler: ImapHandler
    ):
        self.login = login
        self.smtp_handler = smtp_handler
        self.imap_handler = imap_handler

    def __eq__(self, value):
        return isinstance(value, self.__class__) and self.login == value.login

    def __hash__(self):
        return hash(self.login)
