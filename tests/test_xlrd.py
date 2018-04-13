#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import unittest

import xlrd

from easy_atom import helpers


class TestRegex(unittest.TestCase):
    def test_xls_extract_lpp_info(self):
        logger = logging.getLogger('tests')
        filename = "down/LPP_TDB476.xls"
        workbook = xlrd.open_workbook(filename)
        all_worksheets = workbook.sheet_names()

        # test nb sheet
        self.assertEqual(1, len(all_worksheets))

        # test nom sheet
        worksheet = workbook.sheet_by_index(0)
        self.assertEqual('TBD', worksheet.name)

        # test nb lignes significatives
        self.assertEqual(497, worksheet.nrows)

        # version a examiner
        version = 430

        # recuperation des infos sur les versions
        d = {}
        for rownum in range(worksheet.nrows):
            vals = worksheet.row_values(rownum)

            try:
                d[int(vals[0])] = vals
            except:
                pass

        # 6 valeurs pour chaque version
        self.assertEqual(6, len(d[version]))

        # test du titre/chapitre
        chap = d[version][1].replace('\n', ' ').strip()
        self.assertEqual('T1 ch1 et ch2 T2 ch3 et ch7 T3 ch1 et ch4', chap)

        # test de la date
        date_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(d[version][3], workbook.datemode))
        logger.info(date_as_datetime)
        self.assertEqual('2016-12-13T00:00:00', date_as_datetime.isoformat(sep='T'))


if __name__ == '__main__':
    loggers = helpers.stdout_logger(['tests'], logging.DEBUG)
    unittest.main()
