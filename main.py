import configparser
import aiosmtpd
import sys
from pathlib import Path
from time import sleep
import logging
from typing import Dict, List

from user_handlers import SmtpHandler, ImapHandler, MailUser
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.smtp import Envelope

logging.getLogger().setLevel(logging.INFO)

logging.info("Starting program...")


class LocalSmtpHandler:
    """Class for handling SMTP requests from local server"""

    def __init__(self):
        self.mail_users: Dict[
            str, MailUser
        ] = {}  # dict of users with username and handler for each user.

    def load_users(self, config: configparser.ConfigParser) -> None:
        """Loads users from config file

        Args:
            config (configparser.ConfigParser): Config file
        """
        try:
            list_emails = config.get("local", "email_list"). \
                replace(" ", "").split(",")

            logging.info("Loaded users from config file")
            logging.debug(f"Loaded users from config file {list_emails}")

        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            raise ValueError(f"Error reading config file: {e}") from e

        loaded_users: Dict[str, MailUser] = {}
        for email in list_emails:
            # TODO replace try by if and logging
            try:

                smtp_handler = SmtpHandler.load_smtp(config, email)
                imap_handler = ImapHandler.load_imap(config, email)

                if smtp_handler is None and imap_handler is None:
                    raise ValueError
                elif smtp_handler is None:
                    logging.warning(
                        f"SMTP handler missing for {email}. Program will continue."
                    )
                elif imap_handler is None:
                    logging.warning(
                        f"IMAP handler missing for {email}. Program will continue"
                    )

                temp_mail_user = MailUser(email, smtp_handler, imap_handler)
                loaded_users[email] = temp_mail_user
            except ValueError:
                logging.error(
                    f"No SMTP and IMAP handlers found for email {email}. Exiting program."
                )
                sys.exit(1)
        self.mail_users = loaded_users

    async def handle_data(
            self, server: SMTPServer,
            session: object,
            envelope: Envelope) -> str:
        """Handle DATA command from SMTP server.
        #TODO check this tech  aiosmtpd.handlers.Proxy
        Args:
            server (object): SMTP server object
            session (object): SMTP session object
            envelope (object): SMTP envelope object

        Returns:
            str: Response code

        """

        email_from: str = envelope.mail_from
        emails_to: List[str] = envelope.rcpt_tos
        content: bytes = envelope.original_content
        refused_recipients: Dict[str, str] = {}

        try:
            mail_user = self.mail_users[email_from]
        except KeyError:
            logging.error(f"Error: From {email_from} not in config file")
            return "550 User not found"

        if mail_user.smtp_handler:
            mail_user.smtp_handler.send_email(emails_to, content)
        if mail_user.imap_handler:
            mail_user.imap_handler.store_email(content)

        if refused_recipients:
            return f"553 Recipients refused: {refused_recipients}"
        else:
            return "250 Message accepted for delivery"


# TODO: Test it and make it work with real server and config file.
class UTF8Controller(Controller):
    """Allow UTF8 in SMTP server"""

    def factory(self):
        # TODO remoteaddr not filled!
        return SMTPServer(self.handler, decode_data=True, enable_SMTPUTF8=True)


if len(sys.argv) == 2:
    config_path = sys.argv[1]
else:
    config_path = Path(sys.path[0]) / "config.ini"
if not Path(config_path).exists():
    raise OSError(f"Config file not found: {config_path}")

with open(
        config_path, "r"
) as f:  # Use context manager  to automatically close the file after reading
    config = configparser.ConfigParser()
    config.read_file(f)
    logging.info("Config Loaded")

if __name__ == "__main__":
    local_handler = LocalSmtpHandler()
    local_handler.load_users(config)

    if config.getboolean("local", "use_utf8"):
        controller = UTF8Controller(
            local_handler,
            hostname=config.get("local", "host"),
            port=config.getint("local", "port"),
        )
    else:
        controller = Controller(
            local_handler,
            hostname=config.get("local", "host"),
            port=config.getint("local", "port"),
        )
    try:
        controller.start()
        logging.info("Server started.")
        controller.loop.run_forever()
        while controller.loop.is_running():
            # go main thread to sleep...
            # maybe need fix?
            sleep(0.2)

    except KeyboardInterrupt:
        controller.stop()
        logging.info("Exiting")
