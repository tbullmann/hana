from hana.h5dict import load_dict_from_hdf5
from hana.plotting import annotate_x_bar

import h5py
import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate
from scipy.spatial.distance import squareform, pdist

import logging
logging.basicConfig(level=logging.DEBUG)


HIDENS_ELECTRODES_FILE = 'data/hidens_electrodes.h5'
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
        logging.info ('Peak at %f, with half width domain %f ~ %f' % (x_peak, min(domain), max(domain)))
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


def neighborhood_statistics(delay, neighbors, ddof=1):
    """
    Calculates the mean and average squared deviation for a neighborhood around each electrode.
    Note: The average squared deviation is normally calculated as x.sum() / N, where N = len(x). However, in standard
    statistical practice, ddof=1 provides an unbiased estimator of the variance of the infinite population. See
    documentation for numpy.std function.
    :param delay:
    :param neighbors:
    :param ddof:
    :return:
    """
    # Calculate mean delay, and std_delay
    sum_neighbors = sum(neighbors)
    mean_delay = np.divide(np.dot(delay, neighbors), sum_neighbors)
    diff_delay = delay - mean_delay
    var_delay = np.divide(np.dot(np.power(diff_delay, 2), neighbors), sum_neighbors - ddof)
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


def load_traces(filename):
    """
    Load traces for each electrode of the spike triggered average for a single neuron from a hdf5 file.
    :param filename: path and name of the hdf5 file
    :return: V: recordings as an array with the shape electrodes x time
    :return: t: time in s, or None
    :return: x, y: coordinates of the recording electrodes
    :return: trigger, neuron: index of recording electrode and corresponding neuron, if spike triggered averaging was
    performed otherwise None
    """
    file = h5py.File(filename, 'r')
    V = get_variable(file, 'V')
    t = get_variable(file, 't')
    x = get_variable(file, 'x')
    y = get_variable(file, 'y')
    trigger = get_variable(file, 'trigger')
    neuron = get_variable(file, 'neuron')
    logging.info('Load file %s with variables %s' % (filename, file.keys()))
    return V, t, x, y, trigger, neuron


def get_variable(file, key): return np.array(file[key] if key in file.keys() else None)


def load_timeseries(filename):
    """Load time series as a dictionary indexed by neuron from hdf5 file"""
    timeseries = load_dict_from_hdf5(filename)
    return timeseries


def load_positions(hdf5_filename):
    """Loads electrode positions"""
    pos = load_dict_from_hdf5(hdf5_filename)
    return np.rec.fromarrays((pos['x'], pos['y']), dtype=[('x', 'f4'), ('y', 'f4')])


def interval_of_timeseries (timeseries):
    first, last = [], []
    for neuron in timeseries:
        first.append (min(timeseries[neuron]))
        last.append(max(timeseries[neuron]))
    return min(first), max(last)


def partial_timeseries (timeseries, interval=0.1):

    begin, end = interval_of_timeseries(timeseries)

    if interval is not tuple:
        partial_begin, partial_end = (begin, (end-begin) * interval)
    else:
        partial_begin, partial_end = interval

    for neuron in timeseries:
        timeseries[neuron] = timeseries[neuron][np.logical_and(timeseries[neuron]>partial_begin,timeseries[neuron]<partial_end)]

    logging.info('Partial timeseries spanning %d~%d [s] of total %d~%d [s]' % (partial_begin, partial_end, begin, end))
    return timeseries