import h5py
import numpy as np
import scipy.io as sio
import logging

from hana.h5dict import save_dict_to_hdf5, load_dict_from_hdf5
from hana.structure import load_neurites
from publication.plotting import FIGURE_ARBORS_FILE, FIGURE_EVENTS_FILE

logging.basicConfig(level=logging.DEBUG)


def load_events(filename):
    """Loads spiking events from matlab file with frame(=20000*ts) and neuron index in all_events"""
    data = sio.loadmat(filename)["all_events"]
    timestamp = data[0][0][0][0].astype('f8') / 20000.0
    neuron = data[0][0][1][0]
    array = np.rec.fromarrays((timestamp, neuron), dtype=[('time', 'f8'), ('id', 'i4')])
    array.sort(order=['time'])
    return array


def events_to_timeseries(events):
    """Converts events consisting of tupels (time, neuron) to a dictonary with neuron as key and timeseries as value"""
    times, neurons = zip(*events)
    unique_neurons = np.unique(neurons)
    logging.info("uniques neurons: ", unique_neurons)
    timeseries = dict([(neuron, np.array(times)[neurons == neuron]) for neuron in unique_neurons])
    return timeseries


def load_positions(filename):
    """Loads electrode positions"""
    data = sio.loadmat(filename)["hidens_electrodes"]
    x = data[0][0][0][0]
    y = data[0][0][1][0]
    return np.rec.fromarrays((x, y), dtype=[('x', 'f4'), ('y', 'f4')])


def load_neurites(filename):
    """Loads delay map into dictionary"""
    data = sio.loadmat(filename)["arbors"]
    delay = {}
    positive_peak = {}
    for record in data[0]:
        delay[record[0][0][0][0][0]] = record[0][0][1][0]
        positive_peak[record[0][0][0][0][0]] = record[0][0][2][0]

    # Indicies for neurons in events starting at 0, in delays and positive peak from 1 (!)
    # TODO: Fix this BIG BUG in the matlab export script (?) and delete the quick fix below
    delay = {key - 1: value for key, value in delay.items()}
    positive_peak = {key - 1: value for key, value in positive_peak.items()}

    logging.info("Delays: ", delay)

    return delay, positive_peak


def load_traces(filename):
    """

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


def convert_matlab_events_to_hdf5_timeseries():
    """Convert events exported for trigger electrodes to timeseries indexed by neuron ID"""
    trigger_electrode, _, _, _ = load_neurites('../publication/' + FIGURE_ARBORS_FILE)
    events = load_events('../publication/' + FIGURE_EVENTS_FILE)
    timeseries = events_to_timeseries(events)
    print (trigger_electrode.keys())
    print (timeseries.keys())
    # Maybe convert neuron, trigger_electrode from numpy array to int in but the problem goes back to
    # extract_neurites --> structure.extract_all_compartments --> structure.load_traces --> matlab.load_traces so it shoudl
    timeseries = {int(neuron): timeseries[int(trigger_electrode[int(neuron)])] for neuron in trigger_electrode.keys()}
    print (timeseries.keys())
    save_dict_to_hdf5(timeseries, '../publication/data/events.h5')


def load_timeseries(filename):
    """Load time series as a dictionary indexed by neuron from hdf5 file"""
    # TODO: Move load_timeseries and structure.load_traces to hana.recording
    timeseries = load_dict_from_hdf5(filename)
    return timeseries

