import logging
from itertools import product
from os import path, listdir
from re import compile

import numpy as np
from matplotlib import pyplot as plt

from hana.h5dict import save_dict_to_hdf5, load_dict_from_hdf5
from hana.recording import electrode_neighborhoods, find_AIS, segment_axon, segment_dendrite, load_traces, load_positions, HIDENS_ELECTRODES_FILE

def find_overlap(axon_delay, dendrite_peak, presynaptic_neuron, postsynaptic_neuron, thr_peak=10, thr_overlap=0.10):
    delay = np.nan
    overlap_ratio = np.nan
    axon_field = np.greater(axon_delay[presynaptic_neuron], 0)
    dendritic_field = np.greater(dendrite_peak[postsynaptic_neuron], thr_peak)
    overlap = np.logical_and(axon_field, dendritic_field)
    dendrite_size = sum(dendritic_field)
    if dendrite_size > 0:
        overlap_size = sum(overlap)
        overlap_ratio = float(overlap_size) / dendrite_size
        if thr_overlap < overlap_ratio:
            delay = np.mean(axon_delay[presynaptic_neuron][overlap])
            logging.debug('overlap = %1.2f with mean delay = %1.1f [ms]' % (overlap_ratio, delay))
        else:
            logging.debug('overlap = %1.2f too small, no delay assigned' % overlap_ratio)
    return overlap_ratio, delay


def all_overlaps (axon_delay, dendrite_peak, thr_peak=10, thr_overlap=0.10):
    """Compute overlaps"""
    all_overlap_ratios, all_axonal_delays = [], []
    for pair in product(axon_delay, repeat=2):
        presynaptic_neuron, postsynaptic_neuron = pair
        if presynaptic_neuron<>postsynaptic_neuron:
            logging.debug('neuron %d -> neuron %d:' % pair)
            ratio, delay = find_overlap(axon_delay, dendrite_peak, presynaptic_neuron, postsynaptic_neuron,
                                        thr_peak=thr_peak, thr_overlap=thr_overlap)
            if np.isfinite(delay):
                all_overlap_ratios.append((pair, ratio))
                all_axonal_delays.append((pair, delay))
    return dict(all_overlap_ratios), dict(all_axonal_delays)


def extract_all_compartments(neurons, template):

    # Load electrode coordinates and calculate neighborhood
    pos = load_positions(HIDENS_ELECTRODES_FILE)
    neighbors = electrode_neighborhoods(pos)

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

    plt.show()
    logging.info('Neurons with axonal and dendritic arbors:')
    logging.info(extracted_neurons)

    return all_triggers, all_AIS, all_axonal_delays, all_dendritic_return_currents


def extract_compartments(t, V, neighbors):
    # Segment axon and dendrite
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


def get_neurons_from_template(template):
    """Get all neuron indices for the files that match the template string 'data/neuron%d.h5'."""
    neurons = []
    path_to_files, file_template = path.split(template)
    for formatted in listdir(path_to_files):
        result = compile("(.*)".join(file_template.split("%d"))).match(formatted)
        if result: neurons.append(int(result.groups()[0]))
    return neurons


def extract_neurites (template, filename):
    neurons = get_neurons_from_template(template)
    all_triggers, all_AIS, all_axonal_delays, all_dendritic_return_currents =  extract_all_compartments(neurons, template)

    data = {'neurons': np.array(neurons),
            'triggers': all_triggers,
            'AIS': all_AIS,
            'axonal_delays': all_axonal_delays,
            'dendritic_return_currents':all_dendritic_return_currents }
    save_dict_to_hdf5(data, filename)

    logging.info('Saved the following variables to file %s :' % filename)
    logging.info(data.keys())

    # pickle.dump((all_triggers, all_AIS, all_axonal_delays, all_dendritic_return_currents),
    #             open(filename,'wb'))

    logging.info('Saved the neurites of %d neurons to file %s :' % (len(neurons), filename))


def load_compartments(filename):
    """Loads compartments into dictionary"""
    data = load_dict_from_hdf5(filename)
    triggers = data['triggers']
    AIS = data['AIS']
    delays = data['axonal_delays']
    positive_peak = data['dendritic_return_currents']
    return triggers, AIS, delays, positive_peak


def load_neurites(filename):
    """Loads only neurites: axons and dendrites"""
    triggers, AIS, delays, positive_peak = load_compartments(filename)
    return delays, positive_peak



MIN_DENDRITE_ELECTRODES = 0  #TODO: Maybe at least one electrode
MIN_AXON_ELECTRODES = 7  #TODO: Maybe at least one neighborhood
MAX_AXON_ELECTRODES = 5000  #TODO: Maybe over 50% of all electrodes is a good cutoff


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