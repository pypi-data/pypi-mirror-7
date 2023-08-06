# -*- coding: utf-8 -*-


"""Functions returning an IMAP account state

Usage: status [options]

    -c, --config-file=<FILE>    Configuration file (`~/.config/imap-cli` by default)
    -f, --format=<FMT>          Output format
    -v, --verbose               Generate verbose messages
    -h, --help                  Show help options.
    --version                   Print program version.
----
imap-cli-status 0.1.0
Copyright (C) 2014 Romain Soufflet
License MIT
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


from docopt import docopt
import logging
import re
import sys

from imap_cli import config, helpers


log = logging.getLogger('imap-cli-status')

STATUS_RE = r'{dirname} \({messages_count} {recent} {unseen}\)'.format(
    dirname=r'"(?P<dirname>.*)"',
    messages_count=r'MESSAGES (?P<mail_count>\d{1,5})',
    recent=r'RECENT (?P<mail_recent>\d{1,5})',
    unseen=r'UNSEEN (?P<mail_unseen>\d{1,5})',
    )


def status(ctx):
    status_cre = re.compile(STATUS_RE)
    for tags, delimiter, dirname in helpers.list_dir(ctx):
        status, data = ctx.mail_account.status(dirname, '(MESSAGES RECENT UNSEEN)')
        if status != 'OK':
            continue
        status_match = status_cre.match(data[0])
        if status_match is not None:
            group_dict = status_match.groupdict()
            yield {
                'directory': group_dict['dirname'],
                'unseen': group_dict['mail_unseen'],
                'count': group_dict['mail_count'],
                'recent': group_dict['mail_recent'],
            }


def main():
    args = docopt(__doc__[2:], version='IMAP-Cli Status v0.1')
    logging.basicConfig(
        level=logging.DEBUG if args['--verbose'] else logging.WARNING,
        stream=sys.stdout,
    )

    ctx = config.new_context_from_file(args['--config-file'])
    if args['--format'] is not None:
        ctx.format_status = args['--format']

    helpers.connect(ctx)
    for directory_info in status(ctx):
        print ctx.format_status.format(**directory_info)


if __name__ == '__main__':
    sys.exit(main())
