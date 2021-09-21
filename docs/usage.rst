=====
Usage
=====

To use Splintegrate in a Python script::

    from splintegrate import splintegrate
    inFile = 'jw42424024002_01101_00001_nrcb5_rateints.fits'
    outDir = 'output/'
    splint = splintegrate.splint(inFile=inFile,outDir=outDir)
    splint.split()


To use Splintegrate on the command line::

   quick_split jw42424024002_01101_00001_nrcb5_rateints.fits

Here, the default output is :code:`split_output`
