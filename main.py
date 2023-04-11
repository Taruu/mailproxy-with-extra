import asyncio
import configparser
import logging
import os
import smtplib
import sys
from pathlib import Path
from time import sleep
from typing import List, Dict, TypedDict

from user_handlers import SmtpHandler, ImapHandler, MailUser
from aiosmtpd.controller import Controller


class LocalSmtpHandler:
    def __init__(self):
        self.mail_users = {}
        pass

    def load_users(self, config: configparser.ConfigParser):
        list_emails = config.get('local', 'email_list').split(',')
        loaded_users = dict()
        for email in list_emails:
            smtp_handler = SmtpHandler.load_smtp(config, email)
            imap_handler = ImapHandler.load_imap(config, email)
            temp_mail_user = MailUser(email, smtp_handler, imap_handler)
            loaded_users.update({email: temp_mail_user})

        self.mail_users = loaded_users

    async def handle_DATA(self, server, session, envelope):
        refused = {}
        try:

            email = envelope.mail_from
            to = envelope.rcpt_tos
            content = envelope.original_content
            mail_user = self.mail_users.get(email)
            mail_user.smtp_handler.implement_email(to, content)
            mail_user.imap_handler.implement_email(to, content)

        except smtplib.SMTPRecipientsRefused as e:
            return "553 Recipients refused {}".format(" ".join(refused.keys()))
        except smtplib.SMTPResponseException as e:
            return f"{e.smtp_code} {e.smtp_error}"
        else:
            return "250 OK"


if __name__ == '__main__':

    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = Path(sys.path[0]) / "config.ini"
    if not Path(config_path).exists():
        raise Exception(f"Config file not found: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    localHandler = LocalSmtpHandler()
    localHandler.load_users(config)

    controller = Controller(localHandler,
                            hostname=config.get('local', 'host'),
                            port=config.getint('local', 'port')
                            )

    controller.start()
    while controller.loop.is_running():
        sleep(0.2)
