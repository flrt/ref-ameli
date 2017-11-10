import unittest
import re


class TestRegex(unittest.TestCase):
    def test_ccam_compl(self):
        regexcompl = re.compile(r'.*C\w*?m_Note_V(\d+\.?\d*)\.pdf')

        r1 = regexcompl.match("/fileadmin/user_upload/documents/Cam_Note_V46.50.pdf")
        self.assertIsNotNone(r1)
        self.assertEqual(r1.group(1), '46.50')

        r2 = regexcompl.match("/fileadmin/user_upload/documents/Ccam_Note_V46.50.pdf")
        self.assertIsNotNone(r2)
        self.assertEqual(r2.group(1), '46.50')

        r3 = regexcompl.match("/fileadmin/user_upload/documents/Ccam_Note_V47.pdf")
        self.assertIsNotNone(r3)
        self.assertEqual(r3.group(1), '47')

    def test_num_version(self):
        self.assertEqual('{:.02f}'.format(int('4650') / 100), '46.50')
        self.assertEqual('{:.02f}'.format(int('4700') / 100), '47.00')


if __name__ == '__main__':
    unittest.main()
