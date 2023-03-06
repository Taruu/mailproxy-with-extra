# mailproxy

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

mailproxy is a simple SMTP proxy. It receives emails through an unencrypted, unauthenticated SMTP interface and retransmits them through a remote SMTP server that requires modern features such as encryption (SSL, STARTTLS) and/or authentication (SMTP AUTH). mailproxy is primarily useful for enabling email functionality in legacy software that only supports plain SMTP.

# Requirements
[![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/Taruu/mailproxy-with-utils)] (https://www.python.org/downloads/)
[![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Taruu/mailproxy-with-utils/aiosmtpd)] (https://pypi.org/project/aiosmtpd/)


# Usage
1. Create a config file (see below).
2. Run mailproxy from the command line, e.g. `python mailproxy.py`.

By default, mailproxy looks for a `config.ini` in its own directory.
If you have placed your config file elsewhere, you can run mailproxy
using `python mailproxy.py <config_file_path>`.


# Configuration
An example config file for a mailproxy instance that accepts emails locally on port 25 for delivery via Gmail appears below:
```
[local]
host = 127.0.0.1
port = 25

[remote]
host = smtp.gmail.com
port = 465
use_ssl = yes
starttls = no
smtp_auth = yes
smtp_auth_user = USERNAME
smtp_auth_password = PASSWORD
```
