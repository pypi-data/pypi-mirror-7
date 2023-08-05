# -*- coding: utf-8 -*-
# _ds_quantize.py
# This module provides the ds_quantize function.
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

"""This module provides the ds_quantize() function, used to quantize signals
according to a user-specified quantizer characteristic.
"""

import numpy as np

def ds_quantize(y, n=2):
	"""Quantize ``y``

	Quantize y to: 

	 * an odd integer in [-n+1, n-1], if n is even, or
	 * an even integer in [-n+1, n-1], if n is odd.

	This definition gives the same step height for both mid-rise
	and mid-tread quantizers.
	``n`` can be a column vector which specifies how to quantize the 
	rows of ``y``.
	"""
	assert (np.round(n, 0) == n).all() # did we get an int or an array of int?
	if not (hasattr(n, 'shape')): 
		n = n*np.ones(y.shape) # we got an int
	else:
		assert len(n.shape) == 1 or 1 in n.shape
		n = (np.ones((max(n.shape), y.shape[1])).T*n).T

	i = (n % 2 == 0)	
	v = np.zeros(y.shape)
	v[i] = 2*np.floor(0.5*y[i]) + 1 	# mid-rise quantizer
	v[~i] = 2*np.floor(0.5*(y[~i] + 1))	# mid-tread quantizer

	# Limit the output
	L = n - 1
	for m in (-1, 1):
		i = (m*v > L)
		if i.any():
			v[i] = m*L[i]
	return v

def test_ds_quantize():
	"""Test function for ds_quantize()
	"""
	t = np.arange(-3, 3, .2)
	t = t.reshape((1, t.shape[0]))
	y = t
	for _ in range(2):
		y = np.concatenate((y, t), axis=0)
	n = np.array([2, 3, 4])
	re1 = ds_quantize(y, n)
	re2 = np.array([[-1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1., -1.,
	                 -1., -1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
	                  1.,  1.,  1.,  1.],
	                [-2., -2., -2., -2., -2., -2., -2., -2., -2., -2.,  0.,  0.,  0.,
	                  0.,  0.,  0.,  0.,  0.,  0.,  0.,  2.,  2.,  2.,  2.,  2.,  2.,
	                  2.,  2.,  2.,  2.],
	                [-3., -3., -3., -3., -3., -1., -1., -1., -1., -1., -1., -1., -1.,
	                 -1., -1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  3.,
	                  3.,  3.,  3.,  3.]
	               ])
	assert np.allclose(re1, re2, atol=1e-8, rtol=1e-5)

