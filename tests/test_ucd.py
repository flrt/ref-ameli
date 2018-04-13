#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from bs4 import BeautifulSoup
from dbfread import DBF
import re

class TestUCD(unittest.TestCase):
    def test_links(self):
        with open('backup/20180329_UCD.html', 'r') as fin:
            data = fin.read()

            soup = BeautifulSoup(data, "html5lib")
            links = list(filter(lambda x: x.get('href'), soup.find_all('a')))

            #[print(link) for link in links]

            pdf_list = list(filter(lambda x: x.get('href').endswith('.pdf'), links))
            zip_list = list(filter(lambda x: x.get('href').endswith('.zip'), links))
            dbf_list = list(filter(lambda x: x.get('href').endswith('.dbf'), links))

            print("** PDF %d"%len(pdf_list))
            [print(link) for link in pdf_list]
            print("** ZIP %d"%len(pdf_list))
            [print(link) for link in zip_list]
            print("** DBF %d"%len(dbf_list))
            [print(link) for link in dbf_list]

            self.assertEqual(len(pdf_list), 1)
            self.assertEqual(len(zip_list), 2)
            self.assertEqual(len(dbf_list), 5)

    def test_maj(self):
        fn = 'backup/ucd_maj_00403_20180405.dbf'
        database = DBF(fn, encoding='iso8859-1')

        self.assertEquals(31, len(database.records))
        med_regexp = re.compile("(\w+).*")
        med_set=set()
        for r in database.records:
            res_eval = med_regexp.match(r['NOM_COURT'])
            if res_eval:
                med_set.add(res_eval.group(1))

        self.assertEquals(11, len(med_set))



if __name__ == '__main__':
    unittest.main()
