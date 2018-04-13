#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    test simple de l'action mail
"""

import os.path
import unittest

from easy_atom import action


class TestRegex(unittest.TestCase):
    def test_mail_conf(self):
        conffn = 'myconf/mail.json'

        if os.path.exists(conffn):
            a = action.SendMailAction(conf_filename=conffn)
            a.process('unittest mail')

            self.assertIsNotNone(conffn)


if __name__ == '__main__':
    unittest.main()
