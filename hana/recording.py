from scipy.spatial.distance import squareform, pdist

from hana.plotting import annotate_x_bar

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

import logging
logging.basicConfig(level=logging.DEBUG)


MAXIMUM_NEIGHBORS = 7 # sanity check: there are 7 electrodes within 20um on hidens
NEIGHBORHOOD_RADIUS = 20 # neighboring electrodes within 20um
DELAY_EPSILON = 0.050  # resolution for threshold


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


def neighborhood(neighbors, index):
    return np.where(neighbors[index])


# Dendrite segmentation

def __segment_dendrite(t, V, neighbors):
    """
    Verbose segment dendrite function for figures.
    :param V:
    :param t:
    :param neighbors:
    :return: all internal variables
    """
    delay = find_peaks(V, t, negative_peaks=False)   # detect positive peaks
    index_AIS = find_AIS(V)
    mean_delay, std_delay = neighborhood_statistics(delay, neighbors)
    expected_std_delay = mean_std_for_random_delays(delay)

    thr = find_valley(std_delay, expected_std_delay)
    valid_delay = std_delay < thr

    V_AIS = V[index_AIS]
    min_delay, max_delay = half_peak_domain(t, V_AIS)
    return_current_delay = np.logical_and(mean_delay > min_delay, mean_delay < max_delay)

    dendrite = np.multiply(return_current_delay, valid_delay)

    return delay, mean_delay, std_delay, expected_std_delay, thr, valid_delay, index_AIS, min_delay, max_delay, return_current_delay, dendrite


def segment_dendrite(t, V, neighbors):
    """
    Verbose segment dendrite function for figures.
    :param V:
    :param t:
    :param neighbors:
    :return: all internal variables
    """
    delay, mean_delay, std_delay, expected_std_delay, thr, valid_delay, index_AIS, min_delay, max_delay, \
        return_current_delay, dendrite = __segment_dendrite(t, V, neighbors)
    positive_voltage = np.max(V, axis=1)
    dendrite_return_current = restrict_to_compartment(positive_voltage, dendrite)
    return dendrite_return_current

# Axon segmentation

def __segment_axon(t, V, neighbors):
    """
    Verbose segment axon function for figures.
    :param V:
    :param t:
    :param neighbors:
    :return: all internal variables
    """
    delay = find_peaks(V, t)
    index_AIS = find_AIS(V)
    mean_delay, std_delay = neighborhood_statistics(delay, neighbors)
    expected_std_delay = mean_std_for_random_delays(delay)
    thr = find_valley(std_delay, expected_std_delay)
    valid_delay = std_delay < thr
    positive_delay = mean_delay > delay[index_AIS]
    axon = np.multiply(positive_delay, valid_delay)
    return delay, mean_delay, std_delay, expected_std_delay, thr, valid_delay, index_AIS, positive_delay, axon


def segment_axon(t, V, neighbors):
    """
    Verbose segment axon function for figures.
    :param V:
    :param t:
    :param neighbors:
    :return: all internal variables
    """
    _, mean_delay, _, _, _, _, _, _, axon = __segment_axon(t, V, neighbors)
    delay = restrict_to_compartment(mean_delay, axon)
    return delay


def restrict_to_compartment(measurement, compartment):
    """
    Return mean_delay for axon, NaN otherwise.
    :param compartment: boolean array
    :param measurement: array
    :return: delay: array
    """
    delay = measurement
    delay[np.where(np.logical_not(compartment))] = np.NAN
    return delay


def find_AIS(V):
    """
    Electrode with most minimal V corresponding to (proximal) AIS
    :param V: recorded traces
    :return: electrode_index: index of the electrode near to the AIS
    """
    electrode_AIS = np.unravel_index(np.argmin(V), V.shape)[0]
    return electrode_AIS


# Signal detection using neighboring electrodes

def find_valley(std_delay, expected_std_delay):
    # Find valley between peak for axons and peak for random peak at expected_std_delay
    hist, bin_edges = np.histogram(std_delay, bins=np.arange(0, expected_std_delay, step=DELAY_EPSILON))
    index_thr = np.argmin(hist)
    thr = bin_edges[index_thr + 1]
    return thr


def mean_std_for_random_delays(delay):
    # Calculated expected_std_delay assuming a uniform delay distribution
    expected_std_delay = (max(delay) - min(delay)) / np.sqrt(12)
    return expected_std_delay


def neighborhood_statistics(delay, neighbors):
    # Calculate mean delay, and std_delay
    sum_neighbors = sum(neighbors)
    mean_delay = np.divide(np.dot(delay, neighbors), sum_neighbors)
    diff_delay = delay - mean_delay
    var_delay = np.divide(np.dot(np.power(diff_delay, 2), neighbors), sum_neighbors)
    std_delay = np.sqrt(var_delay)
    return mean_delay, std_delay


def find_peaks(V, t, negative_peaks=True):
    """
    Find timing of negative (positive) peaks.
    :param V: matrix containing the trace for each electrode
    :param t: time
    :param negative_peaks: detect negative peaks if true, positive peak otherwise
    :return: delays: delay for each electrode
    """
    indices = np.argmin(V, axis=1) if negative_peaks else np.argmax(V, axis=1)
    delay = t[indices]
    return delay


def electrode_neighborhoods(pos):
    """
    Calculate neighbor matrix from distances between electrodes.
    :param pos: electrode coordinates
    :return: neighbors: square matrix
    """
    pos_as_array = np.asarray(zip(pos.x, pos.y))
    distances = squareform(pdist(pos_as_array, metric='euclidean'))
    neighbors = distances < NEIGHBORHOOD_RADIUS
    sum_neighbors = sum(neighbors)
    assert (max(sum_neighbors)) <= MAXIMUM_NEIGHBORS  # sanity check
    return neighbors