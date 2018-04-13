#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from bs4 import BeautifulSoup


class TestRegex(unittest.TestCase):
    def test_link(self):
        with open('backup/20180329_CCAM.html', 'r') as fin:
            data = fin.read()

            soup = BeautifulSoup(data, "html5lib")
            links = list(filter(lambda x: x.get('href'), soup.find_all('a')))

            self.assertEqual(len(links), 43)

            pdf_list = list(filter(lambda x: x.get('href').endswith('.pdf'), links))
            zip_list = list(filter(lambda x: x.get('href').endswith('.zip'), links))

            self.assertEqual(len(pdf_list), 11)
            self.assertEqual(len(zip_list), 7)


if __name__ == '__main__':
    unittest.main()
