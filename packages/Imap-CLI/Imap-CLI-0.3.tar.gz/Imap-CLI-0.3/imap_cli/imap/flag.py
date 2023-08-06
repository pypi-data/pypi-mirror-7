# -*- coding: utf-8 -*-


"""IMAP lib helpers to manage flag on mails"""


import logging
import os


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def flag(ctx, mail_id=None, flags_str=''):
    if mail_id is None:
        log.error('Can\'t set flag on email {}'.format(mail_id))
        return None
    # TODO(rsoufflet)
    truc = ctx.mail_account.store(mail_id, '+FLAGS', flags_str)
    log.debug(repr(truc))


def unset_flag(ctx, mail_id=None, flags_str=''):
    if mail_id is None:
        log.error('Can\'t set flag on email {}'.format(mail_id))
        return None
    # TODO(rsoufflet)
    truc = ctx.mail_account.store(mail_id, '+FLAGS', flags_str)
    log.debug(repr(truc))
