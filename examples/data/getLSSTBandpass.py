# Grab LSST Bandpasses from the web, and then thin with rel_err = 1.e-5

import galsim
import urllib2
import numpy as np
import os

urldir = 'https://dev.lsstcorp.org/trac/export/29728/sims/throughputs/tags/1.2/baseline/'
for band in 'ugrizy':
    urlfile = urldir + 'total_{0}.dat'.format(band)
    base = os.path.basename(urlfile).replace('total_', 'LSST_')
    if band == 'y':
        urlfile = urldir + 'total_y4.dat'
        base = 'LSST_y.dat'
    file_ = urllib2.urlopen(urlfile)
    x,f = np.loadtxt(file_, unpack=True)
    x1,f1 = galsim.utilities.thin_tabulated_values(x,f,rel_err=1.e-5)
    x2,f2 = galsim.utilities.thin_tabulated_values(x,f,rel_err=1.e-4)
    x3,f3 = galsim.utilities.thin_tabulated_values(x,f,rel_err=1.e-3)
    print "{0} raw size = {1}".format(base,len(x))
    print "    thinned sizes = {0}, {1}, {2}".format(len(x1),len(x2),len(x3))

    with open(base, 'w') as out:
        out.write(
"""# LSST {0}-band total throughput at airmass 1.2
# File taken from https://dev.lsstcorp.org/cgit/LSST/sims/throughputs.git/snapshot/throughputs-1.2.tar.gz
#
#  Thinned by galsim.utilities.thin_tabulated_values to a relative error of 1.e-5
#
# Wavelength(nm)  Throughput(0-1)
""".format(band))
        for i in range(len(x1)):
            out.write(" {0:>10.2f}    {1:>10.5f}\n".format(x1[i], f1[i]))
