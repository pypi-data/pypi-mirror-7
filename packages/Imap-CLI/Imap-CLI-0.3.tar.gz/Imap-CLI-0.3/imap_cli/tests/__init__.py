# -*- coding: utf-8 -*-


"""Imaplib IMAP4_SSL mocking class"""


import mock


example_email_content = '\r\n'.join([
    "From: exampleFrom <example@from.org>",
    "Date: Tue, 03 Jan 1989 09:42:34 +0200",
    "Subject: Mocking IMAP Protocols",
    "To: exampleTo <example@to.org>",
    "MIME-Version: 1.0",
    "Content-Type: text/html;\r\n\tcharset=\"windows-1252\"",
    "Content-Transfer-Encoding: quoted-printable",
    "",
    "EMAIL BODY CONTENT",
])


class ImapConnectionMock(mock.Mock):
    def fetch(self, mails_id_set, request):
        return ('OK', [('1 (FLAGS (\\Seen NonJunk) BODY[HEADER] {1621}', example_email_content), ')'])

    def list(self, *args):
        return ('OK', ['(\\HasNoChildren) "." "Directory_name"', '(\\HasNoChildren) "." "INBOX"'])

    def login(self, *args):
        return ('OK', ['Logged in'])

    def select(self, *args):
        return ('OK', ['1'])

    def search(self, *args):
        return ('OK', ['1'])

    def status(self, *args):
        return ('OK', ['"Directory_name" (MESSAGES 1 RECENT 1 UNSEEN 0)'])
