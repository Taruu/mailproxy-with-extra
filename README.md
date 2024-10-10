# mailproxy

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

mailproxy-with-extra is a simple SMTP and IMAP proxy.

It receives emails through an unencrypted, unauthenticated SMTP/IMAP interface and retransmits them through a remote SMTP server that requires modern features such as encryption (SSL, STARTTLS) and/or authentication. 
mailproxy-with-extra is primarily useful for enabling email functionality in legacy software that only supports plain SMTP, for use better usage you can make store you letter in IMAP.
With IMAP configuration you can easy lookup messages what tou send from legacy software.

mailproxt-with-extra support multiple local account and multiple outbound account, it can be very useful if you need use legacy software in work local network.

# Requirements
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/Taruu/mailproxy-with-utils)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Taruu/mailproxy-with-utils/aiosmtpd)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Taruu/mailproxy-with-utils/systemd-logging)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Taruu/mailproxy-with-utils/python-systemd)

# Usage
```bash
# copy config and edit
cp config_sample.ini config.ini

# install requirements and run app 
python3 -m venv venv
./venv/bin/pip3 install -r requirements.txt 
./venv/bin/python3 main.py
```

By default, mailproxy-with-extra looks for a `config.ini` in its own directory.
If you have placed your config file elsewhere, you can run mailproxy-with-extra
using `python main.py <config_file_path>`.


# Configuration
An example config file for a mailproxy-with-extra instance that accepts emails locally on port 25 for delivery via Gmail and Yandex appears below:
```ini
[local]
host = 127.0.0.1
port = 25
email_list = cat-boy@example.com, fox-girl@example.com # list of local 
use_utf8 = False

# setup local cat-boy@example.com mail to gmail
[smtp_cat-boy@example.com]
host = smtp.gmail.com
port=465
use_ssl=yes
start_tls=no
password = 1234iamcat

# setup local cat-boy@example.com mail to gmail
[imap_cat-boy@example.com]
host = smtp.gmail.com
port = 993
use_ssl = yes
password = 1234iamcat
folder = Sent

# setup local fox-girl@example.com mail to yandex
[smtp_fox-girl@example.com
host = smtp.yandex.ru
port = 465
use_ssl = True
start_tls = False
password = 1234iamfox

[imap_fox-girl@example.com]
host = imap.yandex.ru
port = 993
use_ssl = True
password = 1234iamfox
folder = Sent
```

# Systemd service
Example systemd service:
```editorconfig
[Unit]
After=network.target
Description=Python Service mailproxy


[Service]
User=utils-user #change to own user
WorkingDirectory=/home/utils-user/mailproxy-with-utils/
ExecStart=venv/bin/python3 main.py

[Install]
WantedBy=default.target
```