#!/usr/bin/env python

"""Tests for `splintegrate` package."""


import unittest
import os
import glob
from splintegrate import splintegrate


class TestSplintegrate(unittest.TestCase):
    """Tests for `splintegrate` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        testDir = '/Users/everettschlawin/program_data/splintegrate_data/test_images/'
        testFile = 'jw42424024002_01101_00001_nrcb5_rateints.fits'
        self.testFile = os.path.join(testDir,testFile)
        self.outDir = '/Users/everettschlawin/program_data/splintegrate_data/test_output'

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_intcount(self):
        """Test something."""
        splint = splintegrate.splint(inFile=self.testFile,outDir=self.outDir)
        self.assertEqual(splint.nint, 3)
    
    def test_001_no_input_file(self):
        with self.assertWarns(UserWarning) as cm:
            splint = splintegrate.splint(inFile='gobbledeegook.fits',outDir=self.outDir,overWrite=True)
#        with self.assertRaisesRegex(UserWarning,'No file found') as cm:
#            splint = splintegrate.splint(inFile='gobbledeegook.fits',outDir=self.outDir,overWrite=True)
        self.assertEqual(splint.nint,0)
    
    def test_002_split_files(self):
        splint = splintegrate.splint(inFile=self.testFile,outDir=self.outDir,overWrite=True)
        splint.split()
        fileList = glob.glob(os.path.join(splint.outDir,splint.baseName+'*.fits'))
        self.assertEqual(len(fileList),splint.nint,'Not the same number as output files as nint')
    
    def test_003_check_baseName(self):
        splint = splintegrate.splint(inFile=self.testFile,outDir=self.outDir,overWrite=True)

if __name__ == '__main__':
    unittest.main()
