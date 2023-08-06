#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import imaplib

from i3pystatus.mail import Backend


class IMAP(Backend):
    """
    Checks for mail on a IMAP server
    """

    settings = (
        "host", "port",
        "username", "password",
        "ssl",
        "mailbox",
    )
    required = ("host", "username", "password")

    port = 993
    ssl = True
    mailbox = "INBOX"

    imap_class = imaplib.IMAP4
    connection = None

    def init(self):
        if self.ssl:
            self.imap_class = imaplib.IMAP4_SSL

    def get_connection(self):
        if not self.connection:
            try:
                self.connection = self.imap_class(self.host, self.port)
                self.connection.login(self.username, self.password)
                self.connection.select(self.mailbox)
            except Exception:
                self.connection = None

        try:
            self.connection.select(self.mailbox)
        except Exception:
            self.connection = None

        return self.connection

    @property
    def unread(self):
        conn = self.get_connection()
        if conn:
            return len(conn.search(None, "UnSeen")[1][0].split())
        else:
            sys.stderr.write("no connection")


Backend = IMAP
