from itertools import chain

from scipy.signal import butter, lfilter


def unique_neurons(pair_dict):
    neuron_set = set(list(chain(*list(pair_dict.keys()))))
    return neuron_set


def butter_bandpass(lowcut=100, highcut=3500, fs=20000, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y