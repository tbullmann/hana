from itertools import chain


def unique_neurons(pair_dict):
    neuron_set = set(list(chain(*list(pair_dict.keys()))))
    return neuron_set