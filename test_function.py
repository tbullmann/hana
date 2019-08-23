import matplotlib.pyplot as plt
import numpy as np

from function import timelag_by_for_loop, timelag_by_sawtooth, \
    timelag_hist, timelag, randomize_intervals_by_swapping, randomize_intervals_by_gaussian, surrogate_timeseries, \
    timelag_standardscore, find_peaks, swap_intervals
from plotting import plot_pair_func


def test_swap_intervals ():
    timeseries = np.array([1,2,4,5,7,8,10])
    indicies = np.array([0, 4])
    print timeseries
    print indicies
    print swap_intervals(timeseries,indicies)

def test_timelag(n):
    timeseries1 = np.array(range(n))
    timeseries2 = timeseries1
    print timeseries1, " -> ", timeseries2
    print "timelags by for loop = ", timelag_by_for_loop(timeseries1, timeseries2)
    print "timelags by sawtooth = ", timelag_by_sawtooth(timeseries1, timeseries2)
    timeseries2 = timeseries1+0.1
    print timeseries1, " -> ", timeseries2
    print "timelags by for loop = ", timelag_by_for_loop(timeseries1, timeseries2)
    print "timelags by sawtooth = ", timelag_by_sawtooth(timeseries1, timeseries2)
    timeseries2 = timeseries1-0.2
    print timeseries1, " -> ", timeseries2
    print "timelags by for loop = ", timelag_by_for_loop(timeseries1, timeseries2)
    print "timelags by sawtooth = ", timelag_by_sawtooth(timeseries1, timeseries2)

def test_timelag_hist (n):
    timeseries1 = np.sort(np.random.rand(1, n))[0]
    timeseries2 = np.sort(np.random.rand(1, n))[0]
    print timelag_hist(timelag(timeseries1, timeseries2))[0]

def test_randomize_intervals (n, factor=2):
    timeseries = np.array(np.cumsum(range(n)))
    print "original timeseries    = ", timeseries
    print "gaps                   = ", np.diff(timeseries)
    print "randomized by swapping = ", np.diff(randomize_intervals_by_swapping(timeseries,factor))
    print "randomized by gaussian = ", np.diff(randomize_intervals_by_gaussian(timeseries,factor))

def test_surrogates (n):
    timeseries1 =  np.sort(np.random.rand(n+1))
    timeseries2 = np.sort(0.0002*np.random.rand(n+1) + np.copy(timeseries1)+0.002)
    surrogates = surrogate_timeseries(timeseries2, n=20)
    timelags, std_score, timeseries_hist, surrogates_mean, surrogates_std = timelag_standardscore(timeseries1,
                                                                                         timeseries2, surrogates)
    print "Score: Done."

    score_max, timelags_max, timelag_min, timelag_max = find_peaks (timelags, std_score, thr=10)
    print "Peaks: Done"

    if len(score_max)>0:
        print "peak score   =", score_max[0]
        print "peak timelag =", timelag_max[0]

    plot_pair_func(timelags, timeseries_hist, surrogates_mean, surrogates_std, std_score, 'Testing surrogate timeseries')
    plt.show()


test_swap_intervals()
test_timelag (5)
test_timelag_hist(10000)
test_randomize_intervals(10)
test_surrogates(1000)


