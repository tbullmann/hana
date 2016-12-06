import logging
from itertools import product

import numpy as np


# Structural connectivity from the overlap of axonal and dendritic compartments

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

