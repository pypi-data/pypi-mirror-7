# -*- coding: utf-8 -*-


"""Test config"""


import json
import unittest

from imap_cli import config


class ConfigTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_default_config(self):
        self.ctx = config.new_context()

        for key, value in config.DEFAULT_CONFIG.items():
            assert getattr(self.ctx, key) == value

    def test_config_file_from_example_config_file(self):
        config_example_filename = 'config-example.ini'
        self.ctx = config.new_context_from_file(config_example_filename)

        for key, value in config.DEFAULT_CONFIG.items():
            assert getattr(self.ctx, key) == value

    def test_config_file_from_json(self):
        json_config = ''.join([
            '{"username": "username", "hostname": "imap.example.org", "format_list": "\\nID:         ',
            '{mail_id}\\nFlags:      {flags}\\nFrom:       {mail_from}\\nTo:         {to}\\nDate:       ',
            '{date}\\nSubject:    {subject}", "ssl": true, "limit": 10, "format_status": "{directory:>20} : ',
            '{count:>5} Mails - {unseen:>5} Unseen - {recent:>5} Recent", "password": "secret"}',
        ])
        self.ctx = config.new_context(json.loads(json_config))

        for key, value in config.DEFAULT_CONFIG.items():
            assert getattr(self.ctx, key) == value
