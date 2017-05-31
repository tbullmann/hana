from __future__ import division
from itertools import product, groupby
import numpy as np
import logging

from scipy.special._ufuncs import erfc
from statsmodels.stats.multitest import fdrcorrection

logging.basicConfig(level=logging.DEBUG)


def timelag_by_for_loop (timeseries1, timeseries2):
    """Returns for each event in the first time series the time lags for the event in the second time series
    that precedes, succeeds. Both time series must be sorted in increasing values."""
    preceding_time_lags = []
    succeeding_time_lags = []
    for time1 in timeseries1:
        preceding_time_lags.append(next((time2 - time1 for time2 in reversed(timeseries2) if time2 < time1), []))
        succeeding_time_lags.append(next((time2 - time1 for time2 in timeseries2 if time2 > time1), []))
    return np.sort(np.hstack(preceding_time_lags + succeeding_time_lags))


def sawtooth(timeseries, dtype = np.float32):
    """Sawtooth function expressing the time lag to the next event in the timeseries."""
    epsilon = np.finfo(dtype).eps
    gaps = np.diff(timeseries)
    x = np.column_stack((timeseries[0:-1], timeseries[1:] - epsilon)).flatten()
    y = np.column_stack((gaps, np.zeros_like(gaps))).flatten()
    return [x, y]


def timelag_by_sawtooth (timeseries1, timeseries2):
    """Returns for each event in the first time series the time lags for the event in the second time series
    that precedes, succeeds. Both time series must be sorted in increasing values. Faster than timelag_by_for_loop."""
    preceding_time_lags = - np.interp(np.flipud(-timeseries1), *sawtooth(-np.flipud(timeseries2)), left=np.nan, right=np.nan)
    succeeding_time_lags = np.interp(timeseries1, *sawtooth(timeseries2), left=np.nan, right=np.nan)
    time_lags =  np.sort(np.hstack([preceding_time_lags, succeeding_time_lags]))
    valid_time_lags = (np.ma.fix_invalid(time_lags))
    return np.ma.compressed(valid_time_lags)


timelag = timelag_by_sawtooth


def timelag_hist (timelags, min_timelag=-0.005, max_timelag=0.005, bin_n=100):
    bins = np.linspace(min_timelag, max_timelag, bin_n + 1, endpoint=True)
    return np.histogram(timelags, bins=bins)


def swap_intervals (timeseries, indicies):
    """Swap intervals between adjacent intervals indicated by indicies"""
    intervals = np.diff(timeseries)
    for index in indicies:
        intervals[index], intervals[index+1] = intervals[index+1], intervals[index]
    return np.hstack([timeseries[0], timeseries[0]+np.cumsum(intervals)])


def randomize_intervals_by_swapping (timeseries, factor):
    """Randomize timeseries by randomly swapping adjacent intervals, total factor times the length of timeseries"""
    length = len(timeseries)-1
    times = round(factor*length,0)
    indicies = np.random.randint(0,length-1,int(times))
    return swap_intervals(timeseries,indicies)


def randomize_intervals_by_gaussian (timeseries, factor):
    """Randomize timeseries by assuming indicies make a random walk with (+factor,-factor) of equal probability.
    Much faster than randomize_intervals_by_swapping."""
    gaps = np.diff(timeseries)
    length = len(gaps)
    new_positions = range(length) + np.random.normal(0, factor, length)
    index = np.argsort(new_positions)
    return timeseries[0] + np.hstack((0,np.cumsum(gaps[index])))


randomize_intervals = randomize_intervals_by_gaussian


def surrogate_timeseries (timeseries, n=10, factor=2):
    return [randomize_intervals(timeseries,factor=factor) for i in range(n)]


def timelag_standardscore(timeseries1, timeseries2, surrogates):
    """Returns timelags (midpoints of bins) and standard score as well as the counts from the orginal timeseries
    and mean and standard deviation for the counts from surrogate timeseries"""
    timeseries_hist, bins = timelag_hist(timelag(timeseries1, timeseries2))
    timelags = (bins[:-1] + bins[1:])/2 * 1000  # ms
    surrogates_hist = np.vstack([timelag_hist(timelag(timeseries1, surrogate))[0] for surrogate in surrogates])
    surrogates_mean = surrogates_hist.mean(0)
    surrogates_std = np.std(surrogates_hist, 0)
    try: std_score = (timeseries_hist - surrogates_mean) / surrogates_std
    except ZeroDivisionError: pass
    return timelags, std_score, timeseries_hist, surrogates_mean, surrogates_std


def timeseries_to_surrogates(timeseries, n=10, factor=2):
    """Generating surrogate timeseries (this can take a while)"""
    timeseries_surrogates = dict([(key, surrogate_timeseries(timeseries[key], n=n, factor=factor)) for key in timeseries])
    return timeseries_surrogates


def all_timelag_standardscore (timeseries, timeseries_surrogates):
    """Compute standardscore time histograms"""
    all_std_score = []
    all_timeseries_hist = []
    for pair in product(timeseries, repeat=2):
        timelags, std_score, timeseries_hist,surrogates_mean, surrogates_std \
            = timelag_standardscore(timeseries[pair[0]], timeseries[pair[1]], timeseries_surrogates[pair[1]])
        logging.info ( "Timeseries %d->%d" % pair )
        all_std_score.append((pair, std_score))
        all_timeseries_hist.append((pair, timeseries_hist))
        # if logging.getLogger().getEffectiveLevel()==logging.DEBUG:
        #     plot_pair_func(timelags, timeseries_hist, surrogates_mean, surrogates_std, std_score,
        #                    "Timeseries %d->%d" % pair)
        #     plt.show()
    return timelags, dict(all_std_score), dict(all_timeseries_hist)


def all_peaks (timelags, std_score_dict, structural_delay_dict=None, minimal_synapse_delay=0):
    """
    Return the largest standard score peak for each functional connection, rejecting false positives.
    Implemented is the forward direction, that is looking for peaks at post-synaptic time lags

    After converting z values into p values by p = erfc(z/sqrt(2), the Benjamini-Hochberg procedure is applied to
    control the false discovery rate in the multiple comparisons with a false discover rat fixed at one in all
    comparisons. (alpha = 1/number of standard scores)

    If provided only timelags larger than the sum of axonal and synaptic delay are considered, but the returned
    time lags correspond to the response times to the presynaptic spikes that exclude the axonal delays. This implies
    that only structural connected neuron pairs are tested.

    :param timelags: array with time lags for standard scores
    :param std_score_dict: standard scores indexed by neuron pair
    :param structural_delay_dict: (optional) axonal delays indexed by neuron pair
    :param minimal_synapse_delay: (optional) time lag must be larger than this synapse delay (and axonal delay)
    :return: all_score_max: standard score index py neuron pair
     all_timelag_max: time lags indexed by neuron pair
     z_thr: threshold for standard score
    """
    # TODO Implement reverse directions, that is looking for peaks at pre-synaptic spike time lags
    # TODO Implement detection of negative peaks (inhibitory connections)

    if structural_delay_dict is None:
        pairs = std_score_dict
        offset = lambda pair: 0
    else:  # consider axonal delays
        pairs = structural_delay_dict
        offset = lambda pair: structural_delay_dict[pair]

    # first, collect all z values and determine threshold
    z_values = list()
    for pair in pairs:
        use = timelags > offset(pair)
        std_score = std_score_dict[pair]
        z_values += list(std_score[use])
    z_thr = BH_threshold(z_values)

    # second, determine peak z value and check if above threshold
    all_score_max, all_timelag_max = [], []
    for pair in pairs:
        use = timelags > offset(pair) + minimal_synapse_delay
        std_score = std_score_dict[pair]
        try:
            index_max = np.argmax(std_score[use])
            timelag_max = timelags[use][index_max]
            score_max = std_score[use][index_max]
        except ValueError:  # ValueError: attempt to get argmax of an empty sequence
            score_max = 0
        if score_max > z_thr:   # looking at positive peaks only
            all_score_max.append((pair, score_max))
            all_timelag_max.append((pair, timelag_max))
            logging.info(("Timeseries %d->%d" % pair) +
                         (": max z = %f at %f s" % (score_max, timelag_max)))
        else:
            logging.info(("Timeseries %d->%d" % pair) + ': no peak (above threshold)')

    logging.info('FDR correction %d --> %d with z>%f' % (len(std_score_dict), len(all_score_max), z_thr))

    return dict(all_score_max), dict(all_timelag_max), z_thr


def BH_threshold(z_values):
    """
    Threshold for standard scores by the Benjamini-Hochberg procedure.
    :param z_values: standard scores
    :return: z_threshold: for absolute value of the standard scores, that is abs(z)>z_threshold
    """
    abs_z_values = np.abs(z_values)
    p_values = erfc(abs_z_values / np.sqrt(2))
    FDR = 1 / p_values.size
    rejected, p_values_corrected = fdrcorrection(p_values, alpha=FDR, method='indep', is_sorted=False)
    z_thr = min(abs_z_values[rejected == True])
    return z_thr

