import configparser
import smtplib
import imaplib
from time import time
import logging


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
        # TODO if config not correct or full message!
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
            print(f"Invalid value found for a variable {e}.")
            return None
        except configparser.NoOptionError as e:
            print(f"No option {e.option} found in section {e.section}.")
            return None
        except configparser.NoSectionError as e:
            print(f"Section {e.section} not found.")
            return None
        except configparser.ParsingError:
            print("Error while parsing the configuration file.")
            return None
        
        return ImapHandler(host, port, email, password, use_ssl, folder)
        

    def implement_email(self, rcpt_tos, original_content: bytes):
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
