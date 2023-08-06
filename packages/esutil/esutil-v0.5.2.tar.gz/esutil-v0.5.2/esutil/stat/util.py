"""
Package:
    stat

This is a sub-package of the esutil package. The full reference is esutil.stat

classes
-------
Binner: 
    A class for binning data.

functions
-------
histogram:  
    Calculate the histogram of the input data.  The reverse indices are
    also optionally calculated.  This function behaves similarly to the
    IDL histogram function.  Also has the option to use weights, and
    to tabulate a large number of statistics for each bin.
histogram2d:  
    Histgram two variables.
wmom:  
    Calculate weighted mean and error for the given input data.
wmedian:
    Calculate the weighted median.
sigma_clip:  
    Return the sigma-clipped mean and error for the input data.
interplin:  
    Perform linear interpolation.  This function is less powerful than
    scipy.interpolate.interp1d but behaves like the IDL interpol()
    function, including extrapolation beyond boundaries.
cov2cor(cov)
    Convert the input covariance matrix to a correlation matrix
cor2cov(cor, diagerr)
    Convert a correlation matrix and diagonal errors to a covariance matrix.
cholesky_sample(cov, n, means=None):
    Sample the input covariance using a cholesky decomposition

    This can be used to produce the mean and errors on combined parameters,
    taking into account the covariance.

random_indices:
    Get a unique random selection of indices in [0,imax)

"""
license="""
  Copyright (C) 2010  Erin Sheldon

    This program is free software; you can redistribute it and/or modify it
    under the terms of version 2 of the GNU General Public License as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

from sys import stdout, stderr

# the external C++ code for doing 
# histograms.
try:
    import chist
    have_chist=True
except:
    have_chist=False

# for checking function type, method type
from types import *

try:
    import numpy
    from numpy import zeros, sqrt
    have_numpy=True
except:
    have_numpy=False

import _stat_util

class Binner(dict):
    """
    Bin data and calculate statistics of the bins.

    b = Binner(x, y=None, weights=None)

    Examples
    --------
    For more examples, see the dohist() and calc_stats() methods.
    1 variable:
        b=Binner(x)
        # few ways to calculate hist
        b.dohist(binsize=0.1)
        b.dohist(nbin=10)
        b.dohist(nperbin=10)

        # histogram exists now
        b['hist']

        # calculate more statistics about the bins
        b.calc_stats()
        b['center'], b['low'], b['high']

        # if weights are sent, we also get 'whist' after
        # running calc_stats
        b=Binner(x, weights=w)
        b.dohist(binsize=0.1)
        b.calc_stats()

    2 variables (get averages of the second in the bins of the first):
        b=Binner(x,y)
        b.dohist(nperbin=10)
        b.calc_stats()

        # reverse indices are always calculated when
        # y is sent, so we have the mean values for x,y
        b['xmean'], b['xstd'], b['xerr'], b['xerr2']
        b['ymean'], b['ystd'], b['yerr'], b['yerr2']

    """
    def __init__(self, x, y=None, weights=None):
        self.x = numpy.array(x, ndmin=1, copy=False)
        self.y = y
        self.weights = weights

        self.sort_index = None

        self.xpref=''
        if y is not None:
            self.xpref = 'x'
            self.y = numpy.array(y, ndmin=1, copy=False)
            if self.y.size != self.x.size:
                raise ValueError("y must be same len as x")

        if weights is not None:
            self.weights = numpy.array(weights, ndmin=1, copy=False)
            if self.weights.size != self.x.size:
                raise ValueError("Weights must be same len as data")



    def dohist(self, binsize=None, nbin=None, nperbin=None, min=None, max=None, rev=False, mergelast=True):
        """
        Perform the basic histogram, optionally getting reverse indices. Note
        if weights were sent, reverse indices will always be calculated
        """

        # this method inherited from dict
        self.clear()

        # if y is sent, we use rev to get mean y in the bins
        if self.y is not None:
            rev=True

        # get self['wsort'] and self.dmin, self.dmax
        self._get_minmax_and_indices(min=min, max=max)

        if nperbin is not None:
            self._hist_by_num(nperbin, mergelast=mergelast)
        elif nbin is not None or binsize is not None:
            self._hist_by_binsize_or_nbin(binsize, nbin, rev)
        else:
            raise ValueError("Send binsize or nbin or nperbin")

    def _hist_by_binsize_or_nbin(self, binsize, nbin, rev):

        if binsize is not None:
            nbin = numpy.int64( (self.dmax-self.dmin)/binsize ) + 1
        elif nbin is not None:
            binsize = float(self.dmax-self.dmin)/nbin
        else:
            raise RuntimeError("Expected binsize or nbin")
        self['binsize'] = binsize
        self['nbin'] = nbin

        h,r = self._do_hist(self.x, self.dmin, self['wsort'], binsize, nbin, rev=rev)

        self['hist'] = h
        if r is not None:
            self['rev'] = r

    def _hist_by_num(self, nperbin, mergelast=True):
        
        # histogram indices into array
        # binsize is nperbin
        ind = numpy.arange(self['wsort'].size)
        # already sorted
        inds = ind
        bsize = float(nperbin)
        indmax = ind[-1]
        indmin = 0
        nbin = numpy.int64( (indmax-indmin)/bsize ) + 1
        hist,rev = self._do_hist(ind, 0, inds, bsize, nbin, True)

        # convert the indices in rev to the unlimited, unsorted frame
        self['low'] = numpy.zeros(nbin, dtype='f8')
        self['high'] = numpy.zeros(nbin, dtype='f8')
        for i in xrange(nbin):
            if rev[i] != rev[i+1]:
                w = rev[ rev[i]:rev[i+1] ]

                w = self['wsort'][w]

                rev[ rev[i]:rev[i+1] ] = w

                self['low'][i] = self.x[w[0]]
                self['high'][i] = self.x[w[-1]]


        self['hist'] = hist
        self['rev'] = rev
        self['nperbin'] = nperbin

        if hist[-1] != nperbin and mergelast:
            self._merge_last()

    def _merge_last(self):
        rev=self['rev']

        nbin = self['hist'].size
        if nbin < 2:
            return
        hist=self['hist'][0:nbin-1]
        low=self['low'][0:nbin-1]
        high=self['high'][0:nbin-1]

        hist[-1] = self['hist'][-2] + self['hist'][-1]
        low[-1] = self['low'][-2]
        high[-1] = self['high'][-1]

        r2 = rev[0:rev.size-1]
        r2[nbin-1] = rev[nbin]
        r2[nbin:] = rev[nbin+1:]
        r2[0:nbin] -= 1

        self['hist'] = hist
        self['rev'] = r2
        self['low'] = low
        self['high'] = high

    def _do_hist(self, data, dmin, s, bsize, nbin, rev=False):
        dorev = rev
        if self.weights is not None:
            # force rev so we can add up in bins with weights
            dorev=True

        if have_chist:
            # compute using the external C++ code
            if dorev:
                hist, revind = chist.chist(data, dmin, s, bsize, nbin, dorev)
            else:
                hist         = chist.chist(data, dmin, s, bsize, nbin, dorev)
                revind=None

        else:
            # compute in a python loop

            if dorev:
                revsize = s.size + nbin+1
                revind = numpy.zeros(revsize, dtype='i8')
            else:
                # this is just a dummy variable
                revind=None
            hist = numpy.zeros(nbin, dtype='i8')

            _dohist(data, dmin, s, bsize, hist, revind=revind)

        return hist, revind


    def _get_sort_index(self):
        if self.sort_index is None:
            self.sort_index = self.x.argsort()
        # make it visible too
        self['sort_index'] = self.sort_index

    def _get_minmax_and_indices(self, min=None, max=None):
        """
        Get sort index, min/max, and w, the sorted indices in the specified
        min/max range.
        """
        self._get_sort_index()
        s=self['sort_index']

        dowhere=False
        if min is not None:
            xmin = min
            dowhere=True
        else:
            xmin = self.x[s[0]]


        if max is not None:
            xmax = max
            dowhere=True
        else:
            xmax = self.x[s[-1]]
        
        self.dmin = xmin
        self.dmax = xmax

        self[self.xpref+'min'] = xmin
        self[self.xpref+'max'] = xmax

        if dowhere:
            # where function will preserve order, so subscript with s
            w,=numpy.where( (self.x[s] >= xmin) & (self.x[s] <= xmax) )
            if w.size == 0:
                raise ValueError("No data in specified min/max range: [%s,%s]" % (xmin,xmax))
            self['wsort'] = s[w]
        else:
            self['wsort'] = s

    def calc_stats(self):
        if 'hist' not in self:
            raise ValueError("run dohist first")

        xpref=self.xpref

        nhist = len(self['hist'])
        if 'nperbin' in self:
            # we need to get the actual bin edges
            # from the reverse indices
            pass
        else:
            # if we used a binsize or nbin, we return the
            # edges and center of the bin

            low = numpy.arange(nhist, dtype='f8')
            low = self.dmin + low*self['binsize']

            high = low + self['binsize']
            center = low + 0.5*self['binsize']

            self[xpref+'low'] = low
            self[xpref+'high'] = high
            self[xpref+'center'] = center


        if 'rev' in self:
            revind = self['rev']
            # calculate the mean in the bins
            xmean   = numpy.zeros(nhist) - 9999.0
            xstd    = xmean.copy()
            xerr    = xmean.copy()
            xmedian = xmean.copy()
            if self.y is not None:
                ymean   = xmean.copy()
                ystd    = xmean.copy()
                yerr    = xmean.copy()
                ymedian = xmean.copy()

            if self.weights is not None:
                whist = xmean.copy()
                whist[:] = 0
                wxmean = xmean.copy()
                wxstd  = xmean.copy()
                wxerr  = xmean.copy()
                wxerr2 = xmean.copy()
                if self.y is not None:
                    wymean = xmean.copy()
                    wystd  = xmean.copy()
                    wyerr  = xmean.copy()
                    wyerr2 = xmean.copy()

            for i in xrange(nhist):
                if revind[i] != revind[i+1]:
                    w = revind[ revind[i]:revind[i+1] ]

                    if w.size == 1:
                        xmean[i] = self.x[w[0]]
                        xmedian[i] = xmean[i]
                        xstd[i] = 0
                        xerr[i] = xmean[i]
                        if self.y is not None:
                            ymean[i] = self.y[w[0]]
                            ymedian[i] = ymean[i]
                            ystd[i] = 0
                            yerr[i] = ymean[i]

                        if self.weights is not None:
                            whist[i] = self.x[w[0]]*self.weights[w[0]]
                            wxmean[i] = xmean[i]
                            wxstd[i] = 0
                            wxerr[i] = wxmean[i]
                            wxerr2[i] = wxmean[i]
                            if self.y is not None:
                                wymean[i] = ymean[i]
                                wystd[i] = 0
                                wyerr[i] = wymean[i]
                                wyerr2[i] = wymean[i]


                    else:
                        xmean[i] = self.x[w].mean()
                        xstd[i] = self.x[w].std()
                        xerr[i] = xstd[i]/numpy.sqrt(w.size)
                        xmedian[i] = numpy.median(self.x[w])
                        if self.y is not None:
                            ymean[i] = self.y[w].mean()
                            ystd[i] = self.y[w].std()
                            yerr[i] = ystd[i]/numpy.sqrt(w.size)
                            ymedian[i] = numpy.median(self.y[w])

                        if self.weights is not None:
                            whist[i] = self.weights[w].sum()
                            wm,we,ws=wmom(self.x[w],self.weights[w],sdev=True)
                            j1,we2=wmom(self.x[w],self.weights[w], calcerr=True)
                            wxmean[i] = wm
                            wxstd[i] = ws
                            wxerr[i] = we
                            wxerr2[i] = we2

                            if self.y is not None:
                                wm,we,ws=wmom(self.y[w],self.weights[w],sdev=True)
                                j1,we2=wmom(self.y[w],self.weights[w], calcerr=True)
                                wymean[i] = wm
                                wystd[i] = ws
                                wyerr[i] = we
                                wyerr2[i] = we2




            self[xpref+'mean']   = xmean
            self[xpref+'std']    = xstd
            self[xpref+'err']    = xerr
            self[xpref+'median'] = xmedian
            if self.y is not None:
                self['ymean']   = ymean
                self['ystd']    = ystd
                self['yerr']    = yerr
                self['ymedian'] = ymedian


            if self.weights is not None:
                self['whist']          = whist
                self['w'+xpref+'mean'] = wxmean
                self['w'+xpref+'std']  = wxstd
                self['w'+xpref+'err']  = wxerr
                self['w'+xpref+'err2'] = wxerr2
                if self.y is not None:
                    self['wymean'] = wymean
                    self['wystd']  = wystd
                    self['wyerr']  = wyerr
                    self['wyerr2'] = wyerr2



def histogram(data, weights=None, binsize=1., nbin=None, 
              nperbin=None, mergelast=True,
              min=None, max=None, 
              rev=False, more=False, **keys):
    """
    Calculate the histogram of the input data.  
    
    Similar to IDL histogram.  The reverse indices are also optionally
    calculated.  This routine uses the Binner class in this module for the
    computations.  If you need something more flexible, or need to calculate
    statistics for another variable in the bin, see that class.

    Parameters
    ----------
    data: 
        A numpy array or a sequence that can be converted.

    weights: optional
        A set of weights to use for calculating some statistics.  If weights
        are sent, more=True is implied and a dictionary is returned containing
        a wide variety of statistics, including 'whist' the weighted histogram.
        See docs for the more keyword below.

    binsize: number, optional
        Default 1.0.  The bin size for histogramming.
    nbin: integar, optional
        Choose a number of bins instead of a binsize.  Overrides
        the binsize keyword.
    nperbin: integar, optional
        Choose the number of objects that should fall in each bin.
        Overrides the binsize keyword.  Results in uneven binning.

    min, max:  number, optional
        The min and max data to use from the array.  If these are not sent, min
        and max are determined from the input.


    rev: boolean, optional
        If true, return a tuple 
            h, rev
        Where rev is the reverse indices.   Default is false.  Note if weights
        are sent, or more=True, the result is always a dictionary.  See below.

    more:

        If more is True, or weights are sent, then return more statistics, with
        all outputs in a dictionary. Note more implies rev=True

            keys of the returned dictionary:
                'hist': The histogram.
                'rev':  The reverse indices if the keyword rev=True
                'low': The lower edge of the bins
                'high' Upper edge of the bins.
                'center': Center of the bins
                
            if the keyword rev=True or weights are sent:
                'mean': The mean value in the bin. -9999 if there are
                    no data in the bin.
                'std': The standard deviation in the bin.
                'err': The error on the mean.

            if weights are sent:
                'whist': The weighted histogram.
                'wmean': The weighted mean in the bin.
                'wstd': The weighted standard deviation in the bin.
                'werr': The weighted error in the bin, calculated as
                    sqrt(1/sum(weights))
                'werr2': The weighted error calculated from the
                    weighted variance: 
                      sqrt( (w**2 * (arr-mean)**2).sum() )/weights.sum()


    Using Reverse Indices:
        h,rev = histogram(data, binsize=binsize, rev=True)

        for i in range(h.size):
            if rev[i] != rev[i+1]:
                # data points were found in this bin, get their indices
                indices = rev[ rev[i]:rev[i+1] ]

                # do calculations with data[indices] ...
    """

    if nbin is not None:
        binsize=None

    if more:
        rev=True

    b = Binner(data, weights=weights)
    b.dohist(binsize=binsize, nbin=nbin, nperbin=nperbin, mergelast=mergelast,
             min=min, max=max, rev=rev)

    if more or weights is not None:
        b.calc_stats()

    if weights is not None or more:
        return b

    if rev:
        return b['hist'], b['rev']
    else:
        return b['hist']



def _dohist(data, dmin, s, binsize, hist, revind=None):
    """
    This is the slower python-only implementation
    """
    
    dorev=False
    if revind is not None:
        dorev=True

    nbin=hist.size
    offset = nbin+1
    i=0
    binnum_old = -1

    while i < s.size:
        data_index = s[i]
        if dorev:
            revind[offset] = data_index

        val = data[data_index]

        binnum = numpy.int64( (val-dmin)/binsize )
        if binnum >= 0 and binnum < nbin:
            if binnum > binnum_old:
                tbin = binnum_old + 1
                while tbin <= binnum:
                    if dorev:
                        revind[tbin] = offset
                    tbin += 1

            hist[binnum] += 1
            binnum_old = binnum

        i += 1
        offset += 1

    if dorev:
        # Fill in the last ones
        tbin = binnum_old + 1
        while tbin <= nbin:
            revind[tbin] = revind.size
            tbin += 1






def testhist(doplot=False):
    """
    testhist(doplot=False)

    Run some tests on the histogram function.  If doplot=True is sent, you must
    have the biggles plotting program installed.

    """
    import esutil
    from sys import stdout
    d = numpy.random.random(100000)
    weights = d.copy()
    weights[:] = 0.5

    stdout.write("Testing straight hist\n")
    binsize=0.1
    h=histogram(d,binsize=binsize)
    esutil.misc.colprint(h,names='hist',min=0,max=1)
    stdout.write('\n')

    stdout.write("Testing weights=0.5\n")
    res=histogram(d,binsize=0.1,min=0,max=1,weights=weights)

    form='%12g'
    nform='%12s'
    names=['low','center','high',
           'median',
           'mean','std','err',
           'hist',
           'wmean','wstd','werr','werr2',
           'whist']
    esutil.misc.colprint(res['low'],res['center'],res['high'],
                         res['median'],
                         res['mean'],res['std'],res['err'],
                         res['hist'],
                         res['wmean'],res['wstd'],res['werr'],res['werr2'],
                         res['whist'],
                         names=names, format=form,nformat=nform)

    if doplot:
        import biggles
        plt=biggles.FramedPlot()
        d=biggles.Histogram(res['hist'], x0=min(res['low']), binsize=binsize)
        plt.add(d)
        plt.xlabel = 'data'
        plt.ylabel = 'counts'
        plt.show()



def histogram2d(x, y, 
                nx=None, 
                ny=None, 
                xbin=None, 
                ybin=None, 
                xmin=None, 
                xmax=None, 
                ymin=None, 
                ymax=None, 
                rev=False,
                more=False):
    """
    Name:
        histogram2d
    Purpose:
        Histogram two-dimensional data.

    Calling Sequence:
        histogram2d(x, y, 
                    nx=None, 
                    ny=None, 
                    xbin=None, 
                    ybin=None, 
                    xmin=None, 
                    xmax=None, 
                    ymin=None, 
                    ymax=None, 
                    rev=False,
                    more=False)

    Inputs:
        x,y:  The x and y values for the data.  Must be same length.

    Keywords:
        nx: Number of bins in the x direction.
        ny: Number of bins in the y direction.
        xbin: binsize in the x direction.
        ybin: binsize in the y direction.
        xmin: min range to use in the x direction.
        xmax: max range to use in the x direction.
        ymin: min range to use in the y direction.
        ymax: max range to use in the y direction.
        rev: if True, return a tuple hist,rev

        more: If True, return a dictionary with the histogram in the
            'hist' key, as well as xlow,xhigh,xcenter and other bin
            information.

    """

    x = numpy.array(x, ndmin=1, copy=False)
    y = numpy.array(y, ndmin=1, copy=False)

    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    # binsizes will take precedence
    dobinsizes=False
    donbin=False
    if (xbin != None) and (ybin != None):
        dobinsizes=True
    elif (nx != None) or (ny != None):
        donbin=True
    else:
        raise ValueError("Enter either nx,ny or xbin,ybin")

    if xmin is None:
        xmin=x.min()
    if xmax is None:
        xmax=x.max()
    if ymin is None:
        ymin=y.min()
    if ymax is None:
        ymax=y.max()

    w, = numpy.where( (x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax) )
    if w.size == 0:
        raise ValueError("No data in specified min/max range\n")

    if dobinsizes:
        # determine nx,ny from binsizes
        nx = numpy.int64(  (xmax-xmin)/xbin ) + 1
        ny = numpy.int64(  (ymax-ymin)/ybin ) + 1
    else:
        xbin = (xmax-xmin)/nx
        ybin = (ymax-ymin)/ny

    xind=numpy.floor((x[w]-xmin)*(nx/(xmax-xmin)))
    yind=numpy.floor((y[w]-ymin)*(ny/(ymax-ymin)))

    ind=xind+nx*yind


    result = histogram(ind, min=0, max=nx*ny-1, rev=rev)

    if not more:
        if rev:
            hist, revind=result
            hist = hist.reshape(nx,ny)
            return hist, revind
        else:
            hist = result.reshape(nx,ny)
            return hist
    else:

        output={}
        if rev:
            hist, revind = result
            hist = hist.reshape(nx,ny)
            output['hist'] = hist
            output['rev'] = revind
        else:
            hist = result.reshape(nx,ny)
            output['hist'] = hist


        # create the bin edges and centers
        xlow = numpy.arange(nx, dtype='f8')
        xlow = xmin + xlow*xbin
        xhigh = xlow + xbin
        xcenter = xlow + 0.5*xbin

        ylow = numpy.arange(ny, dtype='f8')
        ylow = ymin + ylow*ybin
        yhigh = ylow + ybin
        ycenter = ylow + 0.5*ybin

        output['xlow'] = xlow
        output['xhigh'] = xhigh
        output['xcenter'] = xcenter

        output['ylow'] = ylow
        output['yhigh'] = yhigh
        output['ycenter'] = ycenter

        output['nx'] = nx
        output['xbin'] = xbin
        output['xmin'] = xmin
        output['xmax'] = xmax

        output['ny'] = ny
        output['ybin'] = ybin
        output['ymin'] = ymin
        output['ymax'] = ymax

        output['ranges'] = ( (xmin,ymin), (xmax,ymax) )
        # useful for biggles
        output['ranges_reverse'] = ( (ymin,xmin), (ymax,xmax) )

        return output

def boxcar_average(x, N):
    """
    convolve the data with a boxcar window of the specified length

    parameters
    ----------
    data: array
        The data
    N: integer
        Size of the window
    """
    from numpy import convolve, ones
    kernel=ones((N,))/N
    return convolve(x, kernel)[(N-1):]


def wmom(arrin, weights_in, inputmean=None, calcerr=False, sdev=False):
    """
    NAME:
      wmom()
      
    PURPOSE:
      Calculate the weighted mean, error, and optionally standard deviation of
      an input array.  By default error is calculated assuming the weights are
      1/err^2, but if you send calcerr=True this assumption is dropped and the
      error is determined from the weighted scatter.

    CALLING SEQUENCE:
     wmean,werr = wmom(arr, weights, inputmean=None, calcerr=False, sdev=False)
    
    INPUTS:
      arr: A numpy array or a sequence that can be converted.
      weights: A set of weights for each elements in array.
    OPTIONAL INPUTS:
      inputmean: 
          An input mean value, around which them mean is calculated.
      calcerr=False: 
          Calculate the weighted error.  By default the error is calculated as
          1/sqrt( weights.sum() ).  If calcerr=True it is calculated as sqrt(
          (w**2 * (arr-mean)**2).sum() )/weights.sum()
      sdev=False: 
          If True, also return the weighted standard deviation as a third
          element in the tuple.

    OUTPUTS:
      wmean, werr: A tuple of the weighted mean and error. If sdev=True the
         tuple will also contain sdev: wmean,werr,wsdev

    REVISION HISTORY:
      Converted from IDL: 2006-10-23. Erin Sheldon, NYU

   """
    
    # no copy made if they are already arrays
    arr = numpy.array(arrin, ndmin=1, copy=False)
    
    # Weights is forced to be type double. All resulting calculations
    # will also be double
    weights = numpy.array(weights_in, ndmin=1, dtype='f8', copy=False)
  
    wtot = weights.sum()
        
    # user has input a mean value
    if inputmean is None:
        wmean = ( weights*arr ).sum()/wtot
    else:
        wmean=float(inputmean)

    # how should error be calculated?
    if calcerr:
        werr2 = ( weights**2 * (arr-wmean)**2 ).sum()
        werr = numpy.sqrt( werr2 )/wtot
    else:
        werr = 1.0/numpy.sqrt(wtot)

    # should output include the weighted standard deviation?
    if sdev:
        wvar = ( weights*(arr-wmean)**2 ).sum()/wtot
        wsdev = numpy.sqrt(wvar)
        return wmean,werr,wsdev
    else:
        return wmean,werr

def wmedian(arr_in, weights_in):
    """
    Calculate the weighted median.  The routine is from

    http://stackoverflow.com/questions/9794558/weighted-median-computation
    """
    # no copy made if they are already arrays
    arr = numpy.array(arr_in, ndmin=1, copy=False)

    sind=arr.argsort()
    
    # Weights is forced to be type double. All resulting calculations
    # will also be double
    weights = numpy.array(weights_in, ndmin=1, dtype='f8', copy=False)

    wtot = weights.sum()
    wtot2 = wtot/2.

    k=0
    sum = wtot-weights[sind[0]]

    while sum > wtot2:
        k += 1
        sum -= weights[sind[k]]

    return arr[sind[k]]


def sigma_clip(arrin, niter=4, nsig=4, get_indices=False, extra={}, 
               verbose=False, silent=False):
    """
    NAME:
      sigma_clip()
      
    PURPOSE:
      Calculate the mean/stdev of an array with sigma clipping. Iterate
      niter times, removing elements that are outside nsig, and recalculating
      mean/stdev.

    CALLING SEQUENCE:
      mean,stdev = sigma_clip(arr, niter=4, nsig=4, extra={})
    
    INPUTS:
      arr: A numpy array or a sequence that can be converted.

    OPTIONAL INPUTS:
      niter: number of iterations, defaults to 4
      nsig: number of sigma, defaults to 4
      get_indices: bool,optional
        if True return mean,stdev,indices

    OUTPUTS:
      mean,stdev: A tuple containing mean and standard deviation.
    OPTIONAL OUTPUTS
      extra={}: Dictionary containing the array of used indices in
         extra['index']

    REVISION HISTORY:
      Converted from IDL: 2006-10-23. Erin Sheldon, NYU
      Minor bug fix to error messaging: 2010-05-28. Brian Gerke, SLAC
      Added silent keyword, to shut off error messages.  BFG 2010-09-13

    """
    arr = numpy.array(arrin, ndmin=1, copy=False)

    index = numpy.arange( arr.size )

    if get_indices:
        res=[None,None,None]
    else:
        res=[None,None]

    for i in numpy.arange(niter):
        m = arr[index].mean()
        s = arr[index].std()

        if verbose:
            stdout.write('iter %s\tnuse: %s\tmean %s\tstdev %s\n' % \
                             (i+1, index.size,m,s))

        clip = nsig*s

        w, = numpy.where( (numpy.abs(arr[index] - m)) < clip )

        if (w.size == 0):
            if (not silent):
                stderr.write("nsig too small. Everything clipped on "
                             "iteration %d\n" % (i+1))
            res[0]=m
            res[1]=s
            return res

        index = index[w]

    # Calculate final stats
    amean = arr[index].mean()
    asig = arr[index].std()

    res[0]=m
    res[1]=s
    extra['index'] = index
    if get_indices:
        res[2] = index

    return res 

def interplin(vin, xin, uin):
    """
    NAME:
      interplin()
      
    PURPOSE:
      Perform 1-d linear interpolation.  Values outside the bounds are
      permitted unlike the scipy.interpolate.interp1d module. They are
      extrapolated from the line between the 0,1 or n-2,n-1 entries.  This
      program is not as powerful as interp1d but it does provide this feature
      which makes it compatible with the IDL interpol() function.

    CALLING SEQUENCE:
      yint = interplin(y, x, u)

    INPUTS:
      y, x:  The y and x values of the data.
      u: The x-values to which will be interpolated.

    REVISION HISTORY:
      Created: 2006-10-24, Erin Sheldon, NYU
    """
    # Make sure inputs are arrays.  Copy only made if they are not.
    v=numpy.array(vin, ndmin=1, copy=False)
    x=numpy.array(xin, ndmin=1, copy=False)
    u=numpy.array(uin, ndmin=1, copy=False)

    # Find closest indices
    xm = x.searchsorted(u) - 1
    
    # searchsorted returns size(array) when the input is larger than xmax
    # Also, we need the index to be less than the last since we interpolate
    # *between* points.
    w, = numpy.where(xm >= (x.size-1))
    if w.size > 0:
        xm[w] = x.size-2

    w, = numpy.where(xm < 0)
    if w.size > 0:
        xm[w] = 0
        
    xmp1 = xm+1
    return (u-x[xm])*(v[xmp1] - v[xm])/(x[xmp1] - x[xm]) + v[xm]


def cor2cov(cor, diagerr):
    """
    Convert a correlation matrix and diagonal errors to a covariance matrix.

    parameters
    ----------
    cor: square array
        The correlation matrix, NxN
    diagerr: array
        The diagonal errors, must be size N

    outputs
    -------
    cov: square array
        The NxN covariance matrix
    """
    if len(diagerr.shape) != 1:
        raise ValueError("expected 1-d diag errors, got %s" % diagerr.shape)
    if len(cor.shape) != 2:
        raise ValueError("expected 2-d correlation matrix, got %s" % cor.shape)
    if cor.shape[0] != cor.shape[1]:
        raise ValueError("expected square correlation matrix, got %s" % cor.shape)
    if cor.shape[0] != diagerr.shape[0]:
        raise ValueError("expected shape agreement for cor (%s) and "
                         "errors (%s) " % (cor.shape,diagerr.shape))

    cov=numpy.zeros(cor.shape, dtype='f8')

    for ix in xrange(diagerr.shape[0]):
        for iy in xrange(diagerr.shape[0]):
            cov[ix,iy] = cor[ix,iy]*diagerr[ix]*diagerr[iy]

    return cov

def cov2cor(cov):
    """
    Convert the input covariance matrix to a correlation matrix

    corr[i,j] = cov[i,j]/sqrt(cov[i,i]*cov[j,j])

    parameters
    ----------
    cov: square array
        An NxN covariance matrix

    outputs
    -------
    cor: square array
        The NxN correlation matrix
    """
    cor = zeros(cov.shape)

    for ix in xrange(cov.shape[0]):
        cxx=cov[ix,ix]
        if cxx <= 0.0:
            raise ValueError("diagonal cov[%d,%d]=%e is not positive" % (ix,ix,cxx))
        for iy in xrange(cov.shape[1]):
            cyy=cov[iy,iy]
            if cyy <= 0.0:
                raise ValueError("diagonal cov[%d,%d]=%e is not positive" % (iy,iy,cyy))
            cor[ix,iy] = cov[ix,iy]/sqrt(cxx*cyy)

    return cor

def cholesky_sample(cov, n, means=None, dist=None):
    """
    Sample the input covariance using a cholesky decomposition.  The idea is
    that in each dimension we draw from the standard distribution, and then
    transform them to have the specified covariance matrix.

    This can be used to produce the mean and errors on combined parameters,
    taking into account the covariance.

    parameters
    ----------
    cov: array
        A 2-d array representing the covariance of the parameters
    n: integer
        The number of random points to generate
    means: array, optional
        The mean values to add to the random points; by default
        the randoms are centered on 0
    dist: function, optional
        The distribution function.  Default is numpy.random.randn.
    
    example:
        cov = array([[1.5,0.3],
                     [0.3,2.7]])
        means=array([5.6, 12.3])
        r = cholesky_sample(cov, 100000, means=means)

        x = (r[0,:]
        erand = (r[1,:]-r[0,:])/(r[1,:]+r[0,:])
        e_mean = erand.mean()
        e_err = erand.std()

    History
        - output is now (npoints,npar) instead of (npar,npoints) to match
        expectation from rec arrays
    """
    if dist is None:
        dist=numpy.random.randn

    npar = cov.shape[0]
    if means is not None:
        nm=len(means)
        if nm != cov.shape[0]:
            raise ValueError("expected %d mean values, got %d" % (npar,nm))

    M = numpy.linalg.cholesky(cov)

    r=dist(npar*n).reshape(npar,n)

    V = numpy.dot(M,r)

    if means is not None:
        for i in xrange(npar):
            V[i,:] += means[i]

    return V.T

def test_cholesky():
    import esutil as eu
    cov=array([[1.0,0.1,0.1],
               [0.1,2.0,0.1],
               [0.1,0.1,3.0]])
    means = [5.0,4.0,8.0]

    n = 100000

    r = cholesky_sample(cov,n,means=means)

    npar = len(means)

    tmp=('mean: %10.6g +/- %10.6g meas: %10.6g +/- %10.6g '
         'emean: %10.6g efrac: %10.6g')
    print 'n:',n
    for i in xrange(npar):
        mtrue=means[i]
        etrue=sqrt(cov[i,i])
        m = r[i,:].mean()
        e = r[i,:].std()
        emean = e/sqrt(n)
        efrac= emean/m
        text = tmp % (mtrue,etrue,m,e,emean,efrac)
        print text

    # sum
    mtrue = means[0] + means[1]
    etrue = sqrt(cov[0,0] + cov[1,1] + 2*cov[0,1])
    sum_0_1 = r[0,:] + r[1,:]
    #eu.plotting.bhist(sum_0_1, binsize=0.2*etrue)
    m_sum_0_1 = sum_0_1.mean()
    e_sum_0_1 = sum_0_1.std()
    emean_sum_0_1 = e_sum_0_1/sqrt(n)
    efrac_sum_0_1 = emean_sum_0_1/m_sum_0_1 
    
    print 'sum 0/1'
    text = tmp % (mtrue,etrue,m_sum_0_1,e_sum_0_1,emean_sum_0_1,efrac_sum_0_1)
    print text

    
    mexp = (means[2]-means[0])/(means[2]+means[0])
    eexp = -9999

    ellip_01 = (r[2,:]-r[0,:])/(r[2,:]+r[0,:])
    m_01 = ellip_01.mean()
    e_01 = ellip_01.std()
    emean_01 = e_01/sqrt(n)
    efrac_01 = emean_01/m_01 
 
    eu.plotting.bhist(ellip_01, binsize=0.2*e_01)

    print 'ellip (mean and err can be different)'
    text = tmp % (mexp,eexp,m_01,e_01,emean_01,efrac_01)
    print text

    m_01, e_01 = eu.stat.sigma_clip(ellip_01,nsig=5)
    emean_01 = e_01/sqrt(n)
    efrac_01 = emean_01/m_01 
    print 'ellip with sigma clip 5'
    text = tmp % (mexp,eexp,m_01,e_01,emean_01,efrac_01)
    print text

    return

    # ratio
    mexp = means[0]/means[1]
    eexp = mexp*sqrt(cov[0,0]/means[0]**2 
                       + cov[1,1]/means[1]**2
                       - 2*cov[0,1]/means[0]/means[1])

    w,=where( numpy.abs(r[1,:] > 1.e-2))
    rat_0_1 = r[0,w]/r[1,w]
    #m_rat_0_1 = rat_0_1.mean()
    #e_rat_0_1 = rat_0_1.std()
    ex={}
    m_rat_0_1, e_rat_0_1 = eu.stat.sigma_clip(rat_0_1,extra=ex,nsig=5)
    w=ex['index']
    eu.plotting.bhist(rat_0_1[w], binsize=0.2*eexp)
    emean_rat_0_1 = e_rat_0_1/sqrt(w.size)
    efrac_rat_0_1 = emean_rat_0_1/m_rat_0_1 
    
    print 'ratio 0/1 (mean and err can be different)'
    text = tmp % (mexp,eexp,m_rat_0_1,e_rat_0_1,emean_rat_0_1,efrac_rat_0_1)
    print text




def random_indices(imax, nrand, **keys):
    """
    Get a unique random selection of indices in [0,imax)

    parameters
    ----------
    imax: 
        range to draw from is [0,imax)
    nrand:
        Number of randoms to create.
    unique:
        If False, the sample will have replacement, and nrand
        can be greater than imax
    seed: int
        A seed for the random number generator
    """
    unique = keys.get('unique',True)
    seed=keys.get('seed',None)
    if seed is None:
        import time
        seed=int( time.time() )

    if not unique:
        return numpy.random.randint(0, imax, nrand)
    else:
        return _stat_util.random_sample(imax, nrand, seed)

