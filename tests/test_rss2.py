import unittest
from lxml import etree
import codecs
from easy_atom import content


class TestXSLT(unittest.TestCase):
    def test_transform(self):
        xslt_root = etree.parse("conf/atom1_to_rss2.xsl")

        atom_xml = etree.parse("feeds/ameli_lpp.xml")
        transform = etree.XSLT(xslt_root)

        rss2_xml = transform(atom_xml)
        encoding = 'utf-8'
        with codecs.open("feeds/ameli_lpp.rss2", "w", encoding) as fout:
            fout.write(content.xml2text(rss2_xml, encoding))


if __name__ == '__main__':
    unittest.main()
