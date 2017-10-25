import datetime
import logging
import pprint
import unittest

import xlrd

import helpers


class TestRegex(unittest.TestXLS):
    def test_xls_extract_lpp_info(self):
        logger = logging.getLogger('tests')
        filename=""
        workbook = xlrd.open_workbook()
        all_worksheets = workbook.sheet_names()
        logger.info(all_worksheets)

        for worksheet_name in all_worksheets:
            worksheet = workbook.sheet_by_name(worksheet_name)
            logger.info(worksheet_name)
            logger.info("Nb row : %d" % worksheet.nrows)

        # for rownum in range(worksheet.nrows):
        #    logger.debug(worksheet.row_values(rownum))


        version = 466
        for rownum in range(workbook.sheet_by_index(0).nrows):
            vals = worksheet.row_values(rownum)
            file_version = 0
            try:
                file_version = int(vals[0])
            except:
                pass

            pp = pprint.PrettyPrinter(indent=4)

            if file_version == version:
                for i in range(len(vals)):
                    print("%d |%s|" % (i, vals[i]))
                    if type(vals[i]) == type(""):
                        strvals = list(filter(lambda x: len(x) > 0, vals[i].split('\n')))
                        print(strvals)
                    if type(vals[i]) == type(0.0):
                        a1_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(vals[i], workbook.datemode))
                        print(a1_as_datetime.strftime("%d-%m-%Y"))

                compl = {'version': version,
                         'titres_chapitres': vals[1].replace('\n', ' ').strip(),
                         'dates_arretes': vals[2].replace('\n', ''),
                         'date_jo': vals[3],
                         'date_ameli': vals[4],
                         'commentaire': vals[5].replace('\n', '').strip()}
                pp.pprint(compl)

                logger.info(compl)


if __name__ == '__main__':
    loggers = helpers.stdout_logger(['tests'], logging.DEBUG)

    unittest.main()
