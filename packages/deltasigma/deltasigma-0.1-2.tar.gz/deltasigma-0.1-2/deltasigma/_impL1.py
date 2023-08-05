# -*- coding: utf-8 -*-
# _impL1.py
# This module provides the impL1 function.
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

"""This module provides the impL1() function, computing the impulse response 
from the comparator output to the comparator input for a given NTF.
"""

import numpy as np
import scipy
from scipy.signal import convolve, dimpulse

from ._padr import padr
from ._utils import _get_num_den, _is_num_den, _is_zpk

def impL1(arg1, n=10):
	"""Impulse response evaluation for NTFs.

	Compute the impulse response from the comparator
	output to the comparator input for the given NTF.

	**Parameters:**

	arg1 : object
	    The NTF, which may be represented as:

	    * ZPK tuple,
	    * num, den tuple,
	    * A, B, C, D tuple,
	    * ABCD matrix,
	    * a scipy LTI object,
	    * a sequence of the tuples of any of the above types (experimental).

	n : int
	    is the (optional) number of time steps (default: 10), resulting in
	    an impulse response with n+1 (default: 11) samples.

	This function is useful when verifying the realization
	of a NTF with a specified topology.

	**Returns:**

	y : ndarray
	    The NTF impulse response

	.. note::

	    In the original implementation of impL1 in delsig, there is a
	    bug: impL1 calls MATLAB's impulse with tfinal=n, which means that
	    the function will return the impulse response evaluated on the times
	    [0, 1, 2 ... n], ie n+1 points. We keep the same behavior here,
	    but we state clearly that n is the number of time steps.

	"""
	if _is_num_den(arg1):
		num, den = arg1
		p = np.roots(den)
	elif _is_zpk(arg1):
		z, p, k = arg1
		num = np.poly(z)
		den = np.poly(p)
	else:
		num, den = _get_num_den(arg1)
		p = np.roots(den)

	num = np.asarray(num)
	den = np.asarray(den)
	p = np.asarray(p)

	lf_den = padr(num, len(p)+1)
	lf_num = lf_den - den
	ts = np.arange(n + 1) # be coherent with the original toolbox
	all_lf = np.concatenate((lf_num, lf_den), axis=1)
	lf_num, lf_den = lf_num.squeeze(), lf_den.squeeze()
	if not np.allclose(np.imag(all_lf), np.zeros(all_lf.shape), atol=1e-9):
		# Complex loop filter
		lfr_den = np.real(conv(lf_den, np.conj(lf_den))).squeeze()
		lfr_num = conv(lf_num, np.conj(lf_den)).squeeze()
		lf_i = (np.real(lfr_num).tolist()[0], lfr_den.tolist()[0], 1)
		lf_q = (np.imag(lfr_num).tolist()[0], lfr_den.tolist()[0], 1)
		_, y = dimpulse(lf_i, t=ts) + 1j*dimpulse(lf_q, t=ts)
	else:
		_, y = dimpulse((lf_num, lf_den, 1), t=ts)
	return y[0].squeeze()

def test_impL1():
	"""Test function for impL1()"""
	sys1 = (np.array([-.4]), np.array([0, 0]), 1) # zpk
	r2 = np.array([0., 0.400000000000000, -0.160000000000000, 0.064000000000000,
	               -0.025600000000000, 0.010240000000000, -0.004096000000000,
	               0.001638400000000, -0.000655360000000, 0.000262144000000,
	               -0.000104857600000])
	r1 = impL1(sys1, n=10)
	assert np.allclose(r1, r2, atol=1e-8, rtol=1e-4)

