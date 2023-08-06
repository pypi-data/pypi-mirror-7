import os
import contextlib
import unittest
import tempfile
import shutil
from path import path	# needs path.py
import latex2edx as l2emod
from latex2edx.main import latex2edx
from StringIO import StringIO

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp('l2etmp')
    yield temp_dir
    shutil.rmtree(temp_dir)

class TestBad_Abox(unittest.TestCase):

    def test_bad_abox1(self):
        testdir = path(l2emod.__file__).parent / 'testtex'  
        fn = testdir / 'example8_badscript.tex'
        print "file %s" % fn
        with make_temp_directory() as tmdir:
            nfn = '%s/%s' % (tmdir, fn.basename())
            os.system('cp %s/* %s' % (testdir, tmdir))
            os.chdir(tmdir)
            try:
                l2e = latex2edx(nfn, output_dir=tmdir)
                l2e.convert()
                err = ""
            except Exception as err:
                print err
            assert('abox located: linenum="43"' in str(err))
            xbfn = nfn[:-4]+'.xbundle'
            self.assertTrue(not os.path.exists(xbfn))

if __name__ == '__main__':
    unittest.main()
