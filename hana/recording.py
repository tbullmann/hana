from hana.plotting import annotate_x_bar

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

import logging
logging.basicConfig(level=logging.DEBUG)


def half_peak_width(x, y): return np.diff(half_peak_domain(x, y))


def half_peak_domain(x, y, negative_peak=True, plot=False):
    """
    Finding the half peak domain (for calculation of the half peak width) using B-spline interpolation.
    Note: Assuming the baseline is 0.
    :param x, y: data describing the function y(x)
    :param negative_peak: True if fitting the negative peak, default False
    :param plot: True if plot for debugging
    :return: domain: a list of two values x' for which y(x')==y_peak/2
    """

    y_peak, index_peak = (min(y), np.argmin(y)) if negative_peak else (max(y), np.argmax(y))
    x_peak = x[index_peak]

    spline_representation = interpolate.splrep(x, y)
    xs, ys, k = spline_representation
    roots = interpolate.sproot((xs, ys - y_peak/2, k))

    index_roots = np.searchsorted(roots, x_peak)
    domain = list(roots[range(index_roots-1,index_roots+1)])

    if plot:
        logging.info ('Peak at %f, with halfwidth domain %f ~ %f' % (x_peak, min(domain), max(domain)))
        xnew = np.arange(min(x), max(x), step=min(np.diff(x))/5)
        ynew = interpolate.splev(xnew, spline_representation)
        plt.plot(x, y, 'x', xnew, ynew, 'b-')
        annotate_x_bar(domain, y_peak / 2)
        plt.show()

    return domain


def peak_peak_width(x, y): return np.diff(peak_peak_domain(x, y))


def peak_peak_domain(x, y, plot=False):
    index_neg_peak = np.argmin(y)
    index_pos_peak = index_neg_peak + np.argmax(y[index_neg_peak:len(x)])  # The positive after the negative peak
    x_neg_peak = x[index_neg_peak]
    y_pos_peak = x[index_pos_peak]
    domain = [x_neg_peak, y_pos_peak]

    if plot:
        logging.info ('Negative peak at %f and positive peak at %f' % (min(domain), max(domain)))
        plt.plot(x, y, 'x:', )
        annotate_x_bar(domain, (max(y) + min(y)) / 2)
        plt.show()

    return domain