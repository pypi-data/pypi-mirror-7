import os
import contextlib
import unittest
import tempfile
import shutil
from lxml import etree
from latex2edx.main import latex2edx
from StringIO import StringIO

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp('l2etmp')
    yield temp_dir
    shutil.rmtree(temp_dir)

class MakeTeX(object):
    def __init__(self, tex):
        buf = """\\documentclass[12pt]{article}\n\\usepackage{edXpsl}\n\n\\begin{document}"""
        buf += tex
        buf += "\\end{document}"
        self.buf = buf

    @property
    def fp(self):
        return StringIO(self.buf)

class TestText(unittest.TestCase):

    def test_text1(self):

        tex = ('\\begin{edXcourse}{1.00x}{1.00x Fall 2013}[url_name=2013_Fall]\n'
               '\\begin{edXchapter}{Unit 1}[start="2013-11-22"]\n'
               '\\begin{edXsection}{Introduction}\n'
               '\\begin{edXtext}{My Name}[url_name=text_url_name]\n'
               'Hello world!\n\n'
               '\\end{edXtext}\n'
               '\\end{edXsection}\n'
               '\\end{edXchapter}\n'
               '\\end{edXcourse}\n'
           )

        with make_temp_directory() as tmdir:
            os.chdir(tmdir)
            fp = MakeTeX(tex).fp
            l2e = latex2edx(tmdir + '/test.tex', fp=fp, do_images=False, output_dir=tmdir)
            l2e.xhtml2xbundle()
            #print "xbundle = "
            #print str(l2e.xb)
            #print

            # self.assertIn(r'<html display_name="My Name" url_name="text_url_name">', str(l2e.xb))

            xml = etree.fromstring(str(l2e.xb))
            html = xml.find('.//html')
            self.assertTrue(html.get('display_name')=='My Name')
            self.assertTrue(html.get('url_name')=='text_url_name')

if __name__ == '__main__':
    unittest.main()
