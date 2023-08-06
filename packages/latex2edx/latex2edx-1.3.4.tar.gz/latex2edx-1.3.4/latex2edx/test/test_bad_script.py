import os
import re
import contextlib
import unittest
import tempfile
import shutil
import json
from path import path	# needs path.py
import latex2edx as l2emod
from latex2edx.main import latex2edx
from StringIO import StringIO

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp('l2etmp')
    yield temp_dir
    shutil.rmtree(temp_dir)

class TestBad_Script(unittest.TestCase):

    def test_bad_script1(self):
        testdir = path(l2emod.__file__).parent / 'testtex'  
        fn = testdir / 'example1_bad_script.tex'
        print "file %s" % fn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, fn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)

            try:
                l2e = latex2edx(nfn, output_dir=tmdir)
                l2e.convert()
            except Exception as err:
                pass

            print "Error = %s" % str(err)
            self.assertTrue(re.search('Error processing element script in file .*\.tex line 82', str(err)))

    def test_bad_script2(self):
        testdir = path(l2emod.__file__).parent / 'testtex'  
        fn = testdir / 'example7_bad_script.tex'
        print "file %s" % fn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, fn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)

            try:
                l2e = latex2edx(nfn, output_dir=tmdir)
                l2e.convert()
            except Exception as err:
                pass

            print "Error = %s" % str(err)
            self.assertTrue(re.search('Error processing element edxincludepy in file .*\.tex line 25', str(err)))

if __name__ == '__main__':
    unittest.main()
