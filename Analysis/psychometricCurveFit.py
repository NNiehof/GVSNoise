"""
Functions for fitting different kinds of psychometric curves to the data.
"""

import numpy as np
from itertools import chain
from scipy.special import erfc
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def success_ratio(x,y):
    """ Success ratio of responses y to stimuli x, and frequency (how many times x was tested).
    Input: stimulus list (or numpy array) x, binary responses y.
    Output: 3 x n numpy array of [x, success ratio, frequency]
    """
    x = np.array(x)
    y = np.array(y)
    xdata = []
    sRatio = []
    freqs = []
    for xval in set(x): # for each x-value, find all responses
        ind = (x == xval)
        yresp = y[ind]
        yfreq = len(yresp)
        ratio = sum(yresp)/yfreq
        xdata.append(xval)
        sRatio.append(ratio)
        freqs.append(yfreq)
    data = np.vstack((xdata,sRatio,freqs))
    return data


def psyfun(x,alpha,beta,gamma,llambda):
    """ Cumulative Gaussian function.

    Arguments
    ---------
        x: array
            x-values for the Gaussian.
        alpha, beta, gamma, llambda:
            Threshold, slope, guess rate and lapse rate parameters.
            
    Returns
    -------
    Cumulative Gaussian with the length of x.
    """
    x = np.array(x)
    psy = gamma + (1-gamma-llambda)* 0.5* erfc(-beta * (x-alpha)/np.sqrt(2))
    psy = gamma + (1-2*gamma)* 0.5* erfc(-beta * (x-alpha)/np.sqrt(2))
    return psy


def psyfunGamEqLamb(x,alpha,beta,gamma):
    """ Cumulative Gaussian function where gamma is assumed equal to lambda.

    Arguments
    ---------
        x: array
            x-values for the Gaussian.
        alpha, beta, gamma:
            Threshold, slope, and guess rate parameters. Lapse rate lambda is assumed to equal the guess rate gamma.
            
    Returns
    -------
    Cumulative Gaussian with the length of x. 
    """
    x = np.array(x)
    psy = gamma + (1-2*gamma)* 0.5* erfc(-beta * (x-alpha)/np.sqrt(2))
    return psy

    
def psyfunAlphaBeta(x,alpha,beta):
    """ Cumulative Gaussian function with mean alpha and slope beta.
    Lapse rate and guess rate are assumed zero, and not fitted. This can be used when
    data sets are such that lapse and guess rates are not informative or cannot be fitted.
    """
    x = np.array(x)
    psy = 0.5 * erfc(-beta * (x-alpha)/np.sqrt(2))
    return psy


def fit_sigmoid(data, xdata_range=None, gammaEqLambda=False,
                bounds=(-np.inf,np.inf), noLapses=False):
    """ Non-linear least squares fit of a cumulative Gaussian function to ydata, as a function of xdata.
    
    Arguments
    ---------
        data: numpy array
            Must be a 3-by-n array with columns [x-values, ratio of successes, frequency] where
            the frequency indicates the number of times the x-value has been presented.
    """
    # unpack data
    x = list(data[0,:])
    ratio = list(data[1,:])
    freqs = list(data[2,:])
    xdata = []
    ydata = []
    for ind in range(len(x)):
        xlist = [x[ind]]
        ylist = [ratio[ind]]
        xdata.append(xlist*int(freqs[ind]))
        ydata.append(ylist*int(freqs[ind]))
    xdata = list(chain.from_iterable(xdata))
    ydata = list(chain.from_iterable(ydata))
    
    if xdata_range is None:
        xdata_range = xdata
    if noLapses:
        params, covar = curve_fit(psyfunAlphaBeta, xdata, ydata, bounds=([-np.inf, 0], np.inf), max_nfev=5000) # bounds set such that slope must be positive (lower bound=0)
        psycurve = psyfunAlphaBeta(xdata_range, params[0], params[1])
    elif gammaEqLambda:
        params, covar = curve_fit(psyfunGamEqLamb, xdata, ydata, absolute_sigma=True, bounds=bounds)
        psycurve = psyfunGamEqLamb(xdata_range, *params)
    elif not gammaEqLambda:
        params, covar = curve_fit(psyfun, xdata, ydata, absolute_sigma=True, bounds=bounds)
        psycurve = psyfun(xdata_range, *params)
    return psycurve, params


def plot_psychometric_curve(ax, stimRange, psy, stimuli, resp_ratio, col):
    ax.plot(stimRange, psy, lw=2.5, color=col)
    ax.plot(stimuli, resp_ratio, 'o', color=col)
    ax.set_xlim([-25,25])
    ax.set_ylim([-0.05,1.05])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)  
