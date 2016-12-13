import logging
from itertools import product

import numpy as np


def find_overlap(axon_delay, dendrite_peak, presynaptic_neuron, postsynaptic_neuron, thr_peak=0, thr_ratio=0.0, thr_overlap=1):
    delay = np.nan
    overlap_size = np.nan
    overlap_ratio = np.nan
    axon_field = np.greater(axon_delay[presynaptic_neuron], 0)
    dendritic_field = np.greater(dendrite_peak[postsynaptic_neuron], thr_peak)
    overlap = np.logical_and(axon_field, dendritic_field)
    dendrite_size = sum(dendritic_field)
    if dendrite_size > 0:
        overlap_size = sum(overlap)
        overlap_ratio = float(overlap_size) / dendrite_size
        if thr_ratio <= overlap_ratio and thr_overlap <= overlap_size:
            delay = np.mean(axon_delay[presynaptic_neuron][overlap])
            logging.debug('overlap at %d electrodes (ratio= %1.2f) with mean delay = %1.1f [ms]' % (overlap_size, overlap_ratio, delay))
        else:
            logging.debug('overlap at %d electrodes (ratio= %1.2f) too small, no delay assigned' % (overlap_size, overlap_ratio) )
    return overlap_size, overlap_ratio, delay


def all_overlaps(axon_delay, dendrite_peak, thr_peak=0, thr_ratio=0, thr_overlap=1):
    """Compute overlaps"""
    all_overlap, all_overlap_ratios, all_axonal_delays = [], [], []
    for pair in product(axon_delay, repeat=2):
        presynaptic_neuron, postsynaptic_neuron = pair
        if presynaptic_neuron != postsynaptic_neuron:
            logging.debug('neuron %d -> neuron %d:' % pair)
            overlap, ratio, delay = find_overlap(axon_delay, dendrite_peak, presynaptic_neuron, postsynaptic_neuron,
                                                 thr_peak=thr_peak, thr_ratio=thr_ratio, thr_overlap=thr_overlap)
            if np.isfinite(delay):
                all_overlap.append((pair, overlap))
                all_overlap_ratios.append((pair, ratio))
                all_axonal_delays.append((pair, delay))
    return dict(all_overlap), dict(all_overlap_ratios), dict(all_axonal_delays)

