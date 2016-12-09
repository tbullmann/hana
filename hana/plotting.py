import numpy as np
from matplotlib import pyplot as plt


def set_axis_hidens(ax, margin=20):
    """
    Standard layout for the multi electrode array.
    :param ax: plots axis handle.
    :param margin: margin around electrodes
    :return: Noting.
    """
    ax.set_aspect('equal')
    # previously the position of all electrodes was used:
    # ax.set_xlim([min(pos.x) - margin, max(pos.x) + margin])
    # ax.set_ylim([min(pos.y) - margin, max(pos.y) + margin])
    # print([min(pos.x) , max(pos.x) ])
    # print([min(pos.y) , max(pos.y) ])
    ax.set_xlim([175.5 - margin, 1908.9+ margin])
    ax.set_ylim([98.123001-margin, 2096.123+margin])
    ax.set_xlabel(r'x [$\mu$m]')
    ax.set_ylabel(r'y [$\mu$m]')
    ax.invert_yaxis()


def annotate_x_bar(domain, y, text='', color = 'r', arrowstyle='|-|'):
    plt.annotate('', (max(domain), y), (min(domain), y),   # for annotations it's the other way round
                 arrowprops={'arrowstyle': arrowstyle, 'color': color, 'shrinkA':  0, 'shrinkB': 0})
    if text: plt.text(max(domain),y, text, verticalalignment='center')


# Plotting networks

def plot_neuron_id(ax, neuron_dict, neuron_pos):
    for neuron in neuron_dict:
        ax.annotate(' %d' % neuron, (neuron_pos.x[neuron], neuron_pos.y[neuron]))


def plot_neuron_points(ax, neuron_dict, neuron_pos):
    for neuron in neuron_dict:
        ax.scatter(neuron_pos.x[neuron], neuron_pos.y[neuron], s=18, marker='o', color='k')


def plot_network(ax, pair_dict, pos, color='k'):
    for (pre, post) in pair_dict:
        ax.annotate('', (pos.x[pre], pos.y[pre]), (pos.x[post], pos.y[post]), arrowprops={'arrowstyle': '<-', 'color':color})


def highlight_connection (ax, neuron_pair, neuron_pos, annotation_text=None, connected=True):
    pre, post = neuron_pair
    linestyle = '-' if connected else ':'
    ax.annotate('', (neuron_pos.x[pre], neuron_pos.y[pre]), (neuron_pos.x[post], neuron_pos.y[post]),
                arrowprops={'arrowstyle': '<-', 'linestyle': linestyle, 'color':'r', 'linewidth':2})
    ax.scatter(neuron_pos.x[pre], neuron_pos.y[pre], s=18, marker='o', color='r')
    ax.scatter(neuron_pos.x[post], neuron_pos.y[post], s=18, marker='o', color='r')
    if annotation_text is not None:
        x = np.mean((neuron_pos.x[pre], neuron_pos.x[post]))
        y = np.mean((neuron_pos.y[pre], neuron_pos.y[post]))
        plt.text(x, y, annotation_text, color = 'r')


# Plotting functional connectivity

def plot_pair_func(timelags, timeseries_hist, surrogates_mean, surrogates_std, std_score, title):
    ax1 = plt.subplot(211)
    plot_timeseries_hist_and_surrogates(ax1, timelags, timeseries_hist, surrogates_mean, surrogates_std)
    ax1.set_title(title)
    ax2 = plt.subplot(212)
    plot_std_score_and_peaks(ax2, timelags, std_score)


def plot_std_score_and_peaks(axis, timelags, std_score, thr=10, peak=None):
    axis.step(timelags, std_score, label="standard score", color='k', linewidth=1, where='mid')
    axis.set_xlim([np.min(timelags), np.max(timelags)])
    axis.set_xlabel("time lag [ms]")
    axis.set_ylabel("(normalized)")
    if thr is not None:
        axis.hlines(thr, np.min(timelags), np.max(timelags), colors='k', linestyles='dashed', label='threshold')
    if peak is not None:
            axis.vlines(peak, thr, np.max(std_score), colors='r', linewidth=4, label='peak')
    axis.legend()


def plot_timeseries_hist_and_surrogates(axis, timelags, timeseries_hist, surrogates_mean, surrogates_std):
    axis.step(timelags, timeseries_hist, label="original histogram", color='k', linewidth=1, where='mid')
    axis.step(timelags, surrogates_mean, label="surrogates (mean)", color='b', linewidth=1, where='mid')
    axis.step(timelags, surrogates_mean - surrogates_std, label="surrogates (std)", color='b', linewidth=1,
              linestyle='dotted', where='mid')
    axis.step(timelags, surrogates_mean + surrogates_std, color='b', linewidth=1, linestyle='dotted', where='mid')
    axis.set_xlim([np.min(timelags), np.max(timelags)])
    axis.set_xlabel("time lag [ms]")
    axis.set_ylabel("count")
    axis.legend()


# Plotting structural connectivity

# Color maps for axon and dendrites
cm_axon = plt.cm.ScalarMappable(cmap=plt.cm.summer, norm=plt.Normalize(vmin=0, vmax=2))
cm_dendrite = plt.cm.ScalarMappable(cmap=plt.cm.gray_r, norm=plt.Normalize(vmin=0, vmax=50))


def plot_neurite(ax, cm, z, pos, alpha=1, thr=0):
    index = np.isfinite(z) & np.greater(z, thr)
    x = pos.x[index]
    y = pos.y[index]
    c = cm.to_rgba(z[index])
    ax.scatter(x, y, 18, c, marker='h', edgecolor='none', alpha=alpha)


def plot_axon(ax, pos, z):
    plot_neurite(ax, cm_axon, z, pos)


def plot_dendrite(ax, pos, z, thr=10):
    plot_neurite(ax, cm_dendrite, z, pos, alpha=0.8, thr=thr)


def plot_neuron_pair(ax, pos, axon_delay, dendrite_peak, neuron_pos, postsynaptic_neuron, presynaptic_neuron, delay):
    plot_axon(ax, pos, axon_delay[presynaptic_neuron])
    plot_dendrite(ax, pos, dendrite_peak[postsynaptic_neuron])
    is_connected = True if np.isfinite(delay) else False
    delay_as_text = ' %1.1f ms' % delay if np.isfinite(delay) else ' not connected!'
    highlight_connection(ax, (presynaptic_neuron, postsynaptic_neuron), neuron_pos,
                         annotation_text=delay_as_text, connected=is_connected)

