=====
Usage
=====

To use Splintegrate in a project::

    from splintegrate import splintegrate
    inFile = 'jw42424024002_01101_00001_nrcb5_rateints.fits'
    outDir = 'output/'
    splint = splintegrate.splint(inFile=inFile,outDir=outDir)
    splint.split()
    