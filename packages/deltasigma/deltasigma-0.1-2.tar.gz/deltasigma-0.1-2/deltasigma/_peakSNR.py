# -*- coding: utf-8 -*-
# _peakSNR.py
# Module providing peakSNR
# Copyright 2013 Giuseppe Venturini
# This file is part of python-deltasigma.
#
# python-deltasigma is a 1:1 Python replacement of Richard Schreier's 
# MATLAB delta sigma toolbox (aka "delsigma"), upon which it is heavily based.
# The delta sigma toolbox is (c) 2009, Richard Schreier.
#
# python-deltasigma is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LICENSE file for the licensing terms.

"""Module providing the peakSNR function.
"""

from __future__ import division
import numpy as np
from numpy.linalg import lstsq

from ._dbv import dbv
from ._config import _debug

def peakSNR(snr, amp):
    """Find the snr peak by fitting a smooth curve to the top end of the SNR 
     vs input amplitude data.
     
     The curve fitted is y = ax + b/(x-c).
     
     Parameters:
     snr: ndarray
     amp: ndarray
     
     Returns:
     
         peak_snr, peak_amp
     
    Notes:
    
     * Both amp and snr are expressed in dB.
     * The two arrays snr and amp should have the same size.
    """

    # Delete garbage data
    for check in (np.isinf, np.isnan):
        i = check(snr)
        snr = np.delete(snr, np.where(i))
        amp = np.delete(amp, np.where(i))
    # sanitize inputs
    for x in (snr, amp):
        if not hasattr(x, 'ndim'):
            x = np.array(x)
        if len(x.shape) > 1 and np.prod(x.shape) != max(x.shape):
            raise ValueError("snr and amp should be vectors (ndim=1)" +
                             "snr.shape: %s, amp.shape: %s" % (snr.shape, amp.shape))
        x = x.squeeze
    # All good
    max_snr = np.max(snr)
    i = np.flatnonzero(snr > max_snr - 10)
    min_i = np.min(i)
    max_i = np.max(i)
    j = np.flatnonzero(snr[min_i:max_i + 1] < max_snr - 15)
    if j:
        max_i = min_i + np.min(j) - 2
        i = np.arange(min_i, max_i + 1)
    snr = 10.0**(snr[i]/20)
    amp = 10.0**(amp[i]/20)
    #n = max(i.shape) # unused variable, REP?
    c = np.max(amp)*1.05
    # fit y = ax + b/(x-c) to the data
    A = np.hstack((amp.reshape(-1, 1), 1.0/(amp.reshape(-1, 1) - c)))
    ab = np.linalg.lstsq(A, snr.reshape((-1, 1)))[0]
    peak_amp = c - np.sqrt(ab[1, 0]/ab[0, 0])
    peak_snr = np.dot(np.array([[peak_amp, 1./(peak_amp-c)]]), ab) #None check mcode
    peak_snr = dbv(peak_snr)
    peak_amp = dbv(peak_amp)
    if _debug:
        import pylab as plt
        pred = np.dot(A, ab)
        hold = plt.ishold()
        plt.hold(True)
        plt.plot(dbv(amp), dbv(pred), '-', color='b')
        plt.hold(hold)
    return peak_snr, peak_amp
    
def test_peakSNR():
    """Test function for peakSNR().
    """
    import scipy.io, pkg_resources
    fname = pkg_resources.resource_filename(__name__, "test_data/test_peak_snr.mat")
    snr = scipy.io.loadmat(fname)['snr'].reshape((-1,))
    amp = scipy.io.loadmat(fname)['amp'].reshape((-1,))
    peak_snr, peak_amp = 76.612340603949761, -3.220409771005124
    ps, pa = peakSNR(snr, amp)
    assert np.allclose(ps, peak_snr, atol=1e-8, rtol=1e-5)
    assert np.allclose(pa, peak_amp, atol=1e-8, rtol=1e-5)

