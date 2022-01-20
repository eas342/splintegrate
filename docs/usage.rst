=====
Usage
=====

To use Splintegrate in a Python script::

    from splintegrate import splintegrate
    inFile = 'jw42424024002_01101_00001_nrcb5_rateints.fits'
    outDir = 'output/'
    splint = splintegrate.splint(inFile=inFile,outDir=outDir)
    splint.split()


To use Splintegrate on the command line for one file::

   quick_split jw42424024002_01101_00001_nrcb5_rateints.fits

Here, the default output is :code:`split_output`

To run it on multiple files, enclose a search string in quotes. For example::

   quick_split "*.fits"

More help on the command line utility may be found with::

   quick_split -h

