import asyncio
import configparser
import logging
import os
from smtpd import SMTPServer
import smtplib
import sys
from pathlib import Path
from time import sleep
from typing import List, Dict, TypedDict

from user_handlers import SmtpHandler, ImapHandler, MailUser
from aiosmtpd.controller import Controller

class LocalSmtpHandler:
    """Class for handling SMTP requests from local server"""

    def __init__(self):
        self.mail_users = {}

    def load_users(self, config: configparser.ConfigParser):
        """Loads users from config file

        Args:
            config (configparser.ConfigParser): Config file

        """
        list_emails = config.get("local", "email_list").split(",")
        loaded_users = {}
        for email in list_emails:
            smtp_handler = SmtpHandler.load_smtp(config, email)
            imap_handler = ImapHandler.load_imap(config, email)
            temp_mail_user = MailUser(email, smtp_handler, imap_handler)
            loaded_users[email] = temp_mail_user


        self.mail_users = loaded_users

    async def handle_data(self, server, session, envelope):
        """Handle DATA command from SMTP server.

        Args:
            server (object): SMTP server object
            session (object): SMTP session object
            envelope (object): SMTP envelope object

        Returns:
            str: Response code

        """
        refused_recipients = {}
        try:
            sender = envelope.mail_from
            recipients = envelope.rcpt_tos
            content = envelope.original_content

            mail_user = self.mail_users.get(sender)
            mail_user.smtp_handler.implement_email(recipients, content)
            mail_user.imap_handler.implement_email(recipients, content)

        except smtplib.SMTPRecipientsRefused as e:
            logging.error(f"Recipients refused: {' '.join(refused_recipients.keys())}")
            return f'553 Recipients refused {"".join(refused_recipients.keys())}'
    
        except smtplib.SMTPResponseException as e:
            logging.error(f"SMTP response exception: {e.smtp_code} {e.smtp_error}")
            return f"{e.smtp_code} {e.smtp_error}"
        else:
            logging.info("Successfully handled DATA command")
            return "250 OK"

class UTF8Controller(Controller): #Allow UTF8 in SMTP server
    def factory(self):
        return SMTPServer(self.handler, decode_data=True, enable_SMTPUTF8=True)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = Path(sys.path[0]) / "config.ini"
    if not Path(config_path).exists():
        raise OSError(f"Config file not found: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    local_handler = LocalSmtpHandler()
    local_handler.load_users(config)

    controller = UTF8Controller(
        local_handler,
        hostname=config.get("local", "host"),
        port=config.getint("local", "port"),
    )

    controller.start()
    while controller.loop.is_running():
        sleep(0.2)