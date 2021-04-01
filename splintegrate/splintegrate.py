"""Main module."""
from astropy.io import fits
from astropy.table import Table
import numpy as np
import glob
import os
import tqdm
import warnings
import pdb
from copy import deepcopy

class splint:
    """
    Splint is the object for taking a multi-integration file and splitting it up
    """
    def __init__(self,inFile=None,outDir=None,overWrite=False,flipToDet=True,
                 detectorName=None):
        """
        Initializes the objects
        
        Parameters
        ----------
        inFile: str
            A path for the file to split
        outDir: str
            The path to the output directory
        overWrite: bool
            Overwrite existing files?
        flipToDet: bool
            Flip to detector coordinates (provisional)?
        detectorName: str or None
            Give a detector name for flipping. If None, it is read from the header automatically
        """
        self.inFile = inFile
        if os.path.exists(self.inFile) == False:
            warnings.warn('No file found. {}'.format(self.inFile))
            self.nint = 0
        else:
            HDUList = fits.open(self.inFile)
            self.head = HDUList[0].header
            if 'INTSTART' not in self.head:
                warnings.warn('INTSTART not found, trying SEGINTST')
                self.int_start_num = self.head['SEGINTST'] + 1
            else:
                self.int_start_num = self.head['INTSTART']
            
            if 'INTEND' not in self.head:
                warnings.warn('INTEND not found, reverting to using NINTS')
                if 'NINTS' not in self.head:
                    warnings.warn('NINTS not found, trying SEGINTED')
                    self.nint = self.head['SEGINTED'] - self.int_start_num + 2  ## number in this file segment
                    self.nint_orig = self.head['EXPINT']
                else:
                    self.nint = self.head['NINTS']
                    self.nint_orig = self.nint
            elif self.head['INTEND'] == 0:
                warnings.warn('INTEND is 0, reverting to using NINTS')
                self.nint = self.head['NINTS']
                self.nint_orig = self.nint
            else:
                self.nint = self.head['INTEND'] - self.int_start_num + 1 ## number in this file segment
                self.nint_orig = self.head['NINTS'] ## original number of integrations in exposure
            
            if 'INT_TIMES' in HDUList:
                self.times_tab = Table(fits.getdata(self.inFile,extname='INT_TIMES'))#HDUList['INT_TIMES'].data)
            else:
                self.times_tab = Table()
        
        self.outDir = outDir
        if os.path.exists(self.outDir) == False:
            os.mkdir(self.outDir)
        
        self.overWrite = overWrite
        self.detectorName = detectorName
        self.flipToDet = flipToDet
        self.baseName = os.path.splitext(os.path.basename(self.inFile))[0]
        
    
    def split(self):
        
        datCube = fits.getdata(self.inFile,extName='SCI')
        
        for i in tqdm.tqdm(np.arange(self.nint)):

            if self.nint == 1:
                _thisint = datCube
            else:
                _thisint = datCube[i]
            
            thisHeader=deepcopy(self.head)
            
            if self.flipToDet == True:
                outDat = flip_data(_thisint,self.head,detectorName=self.detectorName)
                thisHeader['FLIP2DET'] = (True,'Flipped to detector coordinates?')
            else:
                outDat = _thisint
                thisHeader['FLIP2DET'] = (True,'Flipped to detector coordinates?')
            
            tmpStr="{:05d}".format(i+self.int_start_num-1)
            outFile = "{}_I{}.fits".format(self.baseName,tmpStr)
            
            ## since we have split the ints, set nints to 1
            thisHeader['NINTS'] = 1
            thisHeader.insert("NINTS",("ON_NINT",i+self.int_start_num,"This is INT of TOT_NINT"),after=True)
            thisHeader.insert("ON_NINT",("TOT_NINT",self.nint_orig,"Total number of NINT in original exposure"),after=True)
            ## This is the number of ints in the file segment, which could be less than the total
            thisHeader.insert("TOT_NINT",("SEGNINT",self.nint,"Total number of NINT in the segment or file"),after=True)
            
            if len(self.times_tab) == self.nint:
                thisHeader.insert("TIME-OBS",("BJDMID",self.times_tab[i]['int_mid_BJD_TDB'],"Mid-Exposure time (MBJD_TDB)"),after=True)
                thisHeader.insert("BJDMID",("MJDSTART",self.times_tab[i]['int_start_MJD_UTC'],"Exposure start time (MJD_UTC)"),after=True)
            thisHeader['NINTS'] = 1 # set nint to 1
            thisHeader.insert("NINTS",("NINT",1,"Number of ints"))
            thisHeader["COMMENT"] = 'Extracted from a multi-integration file by splintegrate'
            #thisheader["COMMENT"] = 'splintegrate version {}'.format(__version__)
            outHDU = fits.PrimaryHDU(outDat,header=thisHeader)
            
            outPath = os.path.join(self.outDir,outFile)
            if (os.path.exists(outPath) & (self.overWrite == False)):
                print("Found {}. Not overwriting".format(outPath))
            else:
                outHDU.writeto(outPath,overwrite=self.overWrite)
            del outHDU


def flip_data(data,head,detectorName=None):
    """ This flips the detector coordinates from DMS to the Fitswriter way
    
    Perhaps using this module will make things easier in the future:
    https://github.com/spacetelescope/jwst/blob/master/jwst/fits_generator/create_dms_data.py
    
    Parameters
    ----------
    data: numpy array
        The input 2D array
    head: astropy.io.fits header
        Original
    
    Returns
    ----------
    """
    ndim = len(data.shape)
    if detectorName is None:
        if 'DETECTOR' not in head:
            raise Exception("Couldn't find detector name to know how to flip")
        else:
            detectorName = head['DETECTOR']
    if detectorName in ['NRCALONG','NRCA1','NRCA3','NRCB2','NRCB4']:
        if ndim == 2:
            return data[:,::-1]
        elif ndim == 3:
            return data[:,:,::-1]
        else:
            raise Exception("Don't know what to do with {} dimensions".format(ndim))
    elif detectorName in ['NRCBLONG','NRCA2','NRCA4','NRCB1','NRCB3']:
        if ndim == 2:
            return data[::-1,:]
        elif ndim == 3:
            return data[:,::-1,:]
        else:
            raise Exception("Don't know what to do with {} dimensions".format(ndim))
    else:
        raise NotImplementedError("Need to add this detector: {}".format(detectorName))

def get_fileList(self,inFiles):
    """
    Search a file list for a list of files
    
    Parameters
    ----------
    inFiles: str
        A search string (can contain * ) for the files to split
    """
    #self.nFile = len(self.fileList)
    return glob.glob(inFiles)
