import numpy as np
import networkx as nx
from matplotlib import pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG)


def filter(timeseries, axonal_delays, synaptic_delay=0.001, jitter=0.001):
    """
    Shift presynaptic spike by timelag predicted from axonal and synaptic delay. Shifted presynaptic spikes and
    post synaptic spikes that match timing within a jitter form pairs of pre- and post-synaptic events, which could
    be the result of a synaptic transmission. See Izhekevich, 2006 for further explanation.
    :param timeseries: dict of neuron_id: vector of time
    :param axonal_delays: dict of (pre_neuron_id, post_neuron_id): axonal_delay in ms(!)
    :param synaptic_delay: single value, in s(!)
    :param jitter: single value, representing maximum allowed synaptic jitter (+/-), in s(!)
    :return: connected_events: tupels (time, pre_neuron_id), (time, post_neuron_id)
    """
    # TODO: Improve function description, remove unit inconsistencies (ms vs. s)
    # Note: for testing: 9861 -> 10964 with predicted spike time lag 1.266667 ms: 93(candidate) pairs
    connected_events = []
    for pre, post in axonal_delays:
        time_lag = (axonal_delays[pre, post])/1000 + synaptic_delay  # axonal delays in ms -> events in s
        logging.info("Finding spike pairs %d -> %d with predicted spike time lag %f s:" % (pre, post, time_lag))

        _pre = pre-1     # Indicies for neurons in events starting at 0, in delays from 1 (!)
        _post = post-1   # TODO: Fix this BIG BUG!

        if (_pre in timeseries) and (_post in timeseries):
            presynaptic_spikes = timeseries[_pre]
            shifted_presynaptic_spikes = presynaptic_spikes+time_lag
            postsynaptic_spikes = timeseries[_post]
            for offset in (0, 1):  # checking postsynaptic spike before and after shifted presynaptic spike
                position = (np.searchsorted(postsynaptic_spikes, shifted_presynaptic_spikes) - offset).\
                    clip(0, len(postsynaptic_spikes) - 1)
                valid = np.abs(shifted_presynaptic_spikes - postsynaptic_spikes[position]) < jitter
                valid_presynaptic_spikes = presynaptic_spikes[valid]
                valid_postsynaptic_spikes = postsynaptic_spikes[position[valid]]
                new_connected_events = [((pre_time, pre), (post_time, post))
                                        for pre_time, post_time
                                        in (zip(valid_presynaptic_spikes, valid_postsynaptic_spikes))]
                logging.info("From %d candidates add %d valid to %d existing pairs"
                             % (len(position), len(new_connected_events), len(connected_events)))
                connected_events = connected_events + new_connected_events

    logging.info("Total %d pairs" % len(connected_events))
    return connected_events


def combine(connected_events):
    """
    Combine connected events into a graph.
    :param connected_events: see polychronous.filter
    :return: graph_of_connected_events
    """
    graph_of_connected_events = nx.Graph()
    graph_of_connected_events.add_edges_from(connected_events)
    return (graph_of_connected_events)


def plot(graph_of_connected_events):
    """
    Plot polychronous group(s) from the graph of connected events. The events are plotted at their time vs. neuron_id.
    :param graph_of_connected_events: see polychronous.combine
    """
    nx.draw_networkx(graph_of_connected_events,
                     pos={event: event for event in graph_of_connected_events.nodes()},
                     with_labels=False,
                     node_size=50,
                     node_color='black',
                     edge_color='red')
    plt.xlabel("time [s]")
    plt.ylabel("neuron index")


def group(graph_of_connected_events):
    """
    Split the graph into its connected components, each representing a polychronous group.
    :param graph_of_connected_events: see polychronous.combine
    :return: list_of_polychronous_groups
    """
    list_of_polychronous_groups = list(nx.connected_component_subgraphs(graph_of_connected_events))
    return list_of_polychronous_groups


