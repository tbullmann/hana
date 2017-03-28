from hana.h5dict import save_dict_to_hdf5, load_dict_from_hdf5
from hana.recording import load_positions, electrode_neighborhoods, load_traces, find_peaks, \
    neighborhood_statistics, mean_std_for_random_delays, find_valley, half_peak_domain

from os import path, listdir
from re import compile
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


MIN_DENDRITE_ELECTRODES = 0  # The dendrite signal should be seen at least on one electrode
MIN_AXON_ELECTRODES = 7  # The axon should cover at least one neighborhood of electrodes
MAX_AXON_ELECTRODES = 5000  # Not more than half of all electrodes could be a neuron


def extract_all_compartments(neurons, template):
    """
    Read the specified neurons from the files and extract their compartments.
    :param neurons: list of neuron indicies.
    :param template: input filename with format string for the indexing, e.g. 'data/neuron%d.h5'
    :return:
    """

    # Load electrode coordinates and calculate neighborhood
    # pos = load_positions(mea='hidens')
    neighbors = electrode_neighborhoods(mea='hidens')

    # Initialize dictionaries
    extracted_neurons = []
    all_triggers = {}
    all_AIS = {}
    all_axonal_delays = {}
    all_dendritic_return_currents = {}

    for neuron in neurons:
        # Load  data
        V, t, x, y, trigger, _ = load_traces(template % (neuron))
        t *= 1000  # convert to ms

        axon, dendrite, axonal_delay, dendrite_return_current, index_AIS, number_axon_electrodes, \
        number_dendrite_electrodes = extract_compartments(t, V, neighbors)

        if number_dendrite_electrodes> MIN_DENDRITE_ELECTRODES \
                and number_axon_electrodes>MIN_AXON_ELECTRODES and number_axon_electrodes<MAX_AXON_ELECTRODES:

            extracted_neurons.append(int(neuron))
            all_triggers[neuron] = trigger
            all_AIS[neuron] = index_AIS
            all_axonal_delays[neuron] = axonal_delay
            all_dendritic_return_currents[neuron] = dendrite_return_current
        else:
            logging.info('No axonal and dendritic compartment(s).')

    logging.info('Neurons with axonal and dendritic arbors:')
    logging.info(extracted_neurons)

    return all_triggers, all_AIS, all_axonal_delays, all_dendritic_return_currents


def extract_compartments(t, V, neighbors):
    """
    Segment AIS, axon and dendrite of a single neuron from the traces of the spike triggered average.
    :param t: time in ms
    :param V: traces for each electrode
    :param neighbors: adjacency matrix of the electrodes
    """
    index_AIS = find_AIS(V)
    axonal_delay = segment_axon(t, V, neighbors)
    axon = np.isfinite(axonal_delay)
    dendrite_return_current = segment_dendrite(t, V, neighbors)
    dendrite = np.isfinite(dendrite_return_current)
    number_axon_electrodes = sum(axon)
    number_dendrite_electrodes = sum(dendrite)
    logging.info(
        '%d electrodes near axons, %d electrodes near dendrites' % (number_axon_electrodes, number_dendrite_electrodes))
    return axon, dendrite, axonal_delay, dendrite_return_current, index_AIS, number_axon_electrodes, number_dendrite_electrodes


def get_neurons_from_template(template, ignore=None):
    """Get all neuron indices for the files that match the template string, e.g. 'data/neuron%d.h5'."""
    neurons = []
    path_to_files, file_template = path.split(template)
    for formatted in listdir(path_to_files):
        result = compile("(.*)".join(file_template.split("%d"))).match(formatted)
        if result:
            neuron = int(result.groups()[0])
            if ignore:
                if neuron not in ignore:
                    neurons.append(neuron)
            else:
                neurons.append(neuron)
    logging.info('Found files for neurons: {}'.format(neurons))
    return neurons


def extract_and_save_compartments(template, filename, ignore=None):
    """
    Read spike triggered averages for each neurons from the files matching the template, extract the compartments
    and save the result in a single file.
    :param template: input filename with format string for the indexing, e.g. 'data/neuron%d.h5'
    :param filename: output filename, e.g. 'temp/all_neurites.h5'
    :param ignore: list with neurons that should be ignored
    :return:
    """
    neurons = get_neurons_from_template(template, ignore=ignore)
    all_triggers, all_AIS, all_axonal_delays, all_dendritic_return_currents =  extract_all_compartments(neurons, template)

    data = {'neurons': np.array(neurons),
            'triggers': all_triggers,
            'AIS': all_AIS,
            'axonal_delays': all_axonal_delays,
            'dendritic_return_currents':all_dendritic_return_currents }
    save_dict_to_hdf5(data, filename)

    logging.info('Saved the neurites of %d neurons to file %s :' % (len(neurons), filename))
    logging.info(data.keys())


def load_compartments(filename):
    """Loads compartments into dictionary"""
    data = load_dict_from_hdf5(filename)
    triggers = data['triggers']
    AIS = data['AIS']
    delays = data['axonal_delays']
    positive_peak = data['dendritic_return_currents']
    return triggers, AIS, delays, positive_peak


def load_neurites(filename):
    """Loads only neurites: axons and dendrites
    :param filename: filename for file exported by extract_and_save_compartments, e.g. 'temp/all_neurites.h5'
    """
    triggers, AIS, delays, positive_peak = load_compartments(filename)
    return delays, positive_peak


def neuron_position_from_trigger_electrode(pos, trigger):
    """Use position of trigger electrode as position of neuron"""
    import numpy as np
    max_neuron = max(trigger.keys())
    x = np.zeros(max_neuron+1)
    y = np.zeros(max_neuron+1)
    for neuron in trigger:
        trigger_electrode = int(trigger[int(neuron)])
        x[neuron] = pos.x[trigger_electrode]
        y[neuron] = pos.y[trigger_electrode]
    neuron_pos =  np.rec.fromarrays((x, y), dtype=[('x', 'f4'), ('y', 'f4')])
    return neuron_pos


def segment_dendrite_verbose(t, V, neighbors):
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
        return_current_delay, dendrite = segment_dendrite_verbose(t, V, neighbors)
    positive_voltage = np.max(V, axis=1)
    dendrite_return_current = restrict_to_compartment(positive_voltage, dendrite)
    return dendrite_return_current


def segment_axon_verbose(t, V, neighbors):
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
    _, mean_delay, _, _, _, _, _, _, axon = segment_axon_verbose(t, V, neighbors)
    delay = restrict_to_compartment(mean_delay, axon)
    return delay


def restrict_to_compartment(measurement, compartment):
    """
    Return measurement only if electrode recorded a valid signal from this compartment, NaN otherwise.
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