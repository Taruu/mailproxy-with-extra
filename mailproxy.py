import asyncio
import configparser
import logging
import os
import smtplib
import sys
import time
from pathlib import Path
from typing import Dict, Union

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as SMTPServer

import puglogger

logging_config: Dict[str, Union[str, int]] = {
    "log_file": "pugmailproxy.log",
    "log_size": 1000000,
    "log_count": 10,
    "log_level": 20,
}


class UTF8Controller(Controller):
    def factory(self) -> SMTPServer:
        return SMTPServer(self.handler, decode_data=True, enable_SMTPUTF8=True)


class MailProxyHandler:
    def __init__(self, host: str, port: int = 0, auth: dict[str, str] | None = None, use_ssl: bool = False, starttls: bool = False) -> None:
        self._host = host
        self._port = port
        auth = auth or {}
        self._auth_user = auth.get("user") if auth else None
        self._auth_password = auth.get("password") if auth else None
        self._use_ssl = use_ssl
        self._starttls = starttls

    async def _deliver(self, envelope):
        refused = {}
        try:
            with smtplib.SMTP(self._host, self._port) as s:
                if self._use_ssl:
                    s.starttls()

                if self._auth_user and self._auth_password:
                    s.login(self._auth_user, self._auth_password)

                refused = await asyncio.to_thread(s.sendmail, envelope.mail_from, envelope.rcpt_tos, envelope.original_content)

        except (OSError, smtplib.SMTPException) as e:
            puglog.logerr(f"got {e.__class__}")
            # All recipients were refused. If the exception had an associated
            # error code, use it.  Otherwise, fake it with a SMTP 554 status code.
            smtperrcode = getattr(e, "smtp_code", 554)
            smtperrmsg = getattr(e, "smtp_error", e.__class__.__name__.encode())
            errormsg = f"{smtperrcode} {smtperrmsg.decode()}"
            raise smtplib.SMTPResponseException(smtperrcode, errormsg)
        
        except Exception as e:
            puglog.logerr(f"Unexpected error occurred during sendmail: {type(e).__name__}: {e}")


        return refused

    async def handle_DATA(self, server, session, envelope):
        refused = {}
        try:
            refused = await self._deliver(envelope)
        except smtplib.SMTPRecipientsRefused as e:
            puglog.log(f"Got SMTPRecipientsRefused: {refused}")
            return "553 Recipients refused {}".format(" ".join(refused.keys()))
        except smtplib.SMTPResponseException as e:
            return f"{e.smtp_code} {e.smtp_error}"
        else:
            if refused:
                puglog.log(f"Recipients refused: {refused}")
            return "250 OK"


if __name__ == "__main__":
    puglog = puglogger.Logging(
        logFile=str(logging_config["log_file"]),
        logSize=int(logging_config["log_size"]),
        logCount=int(logging_config["log_count"]),
        logLevel=int(logging_config["log_level"]),
    )

    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = Path(sys.path[0]) / "config.ini"
    if not Path(config_path).exists():
        raise Exception(f"Config file not found: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    use_auth = config.getboolean("remote", "smtp_auth", fallback=False)
    if use_auth:
        auth = {
            "user": config.get("remote", "smtp_auth_user"),
            "password": config.get("remote", "smtp_auth_password"),
        }
    else:
        auth = None

controller = UTF8Controller(
    MailProxyHandler(
        host=config.get("remote", "host"),
        port=config.getint("remote", "port", fallback=25),
        auth=auth,
        use_ssl=config.getboolean("remote", "use_ssl", fallback=False),
        starttls=config.getboolean("remote", "starttls", fallback=False),
    ),
    hostname=config.get("local", "host", fallback="127.0.0.1"),
    port=config.getint("local", "port", fallback=25),
)
try:
    controller.start()
    puglog.log(
        "Mail proxy starting on port:{}".format(config.getint("local", "port"))
    )
    while controller.loop.is_running():
        time.sleep(1)
except (KeyboardInterrupt, asyncio.CancelledError):
    controller.stop()
    if callable(getattr(controller, '_cleanup', None)):
        controller._cleanup()
    puglog.logwarn("Mail proxy stopped by user")
except Exception as e:
    puglog.logerr(f"Caught unknown exception: {type(e).__name__}: {e}")
