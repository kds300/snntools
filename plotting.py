import os
import json
import matplotlib.pyplot as plt
import numpy as np
from.data import Database

# setup dir info
with open(
    os.path.join(
        os.path.dirname(__file__),
        'dir_info.json'
    ),
    'r'
) as f:
        dir_info = json.load(f)


FIG_SAVE_DIR = dir_info['FIG_SAVE_DIR']
MPL_STYLE_DIR = dir_info['MPL_STYLE_DIR']


def save_figs(file_name, exts=['pdf', 'png']):
    """Save current pyplot figure in multiple file types.
    """
    for ext in exts:
        plt.savefig(os.path.join(FIG_SAVE_DIR, f"{file_name}.{ext}"))

def add_key_ylabel(key, ax=None):
    """Label y-axis using provided key for the indices, adding gray dashed
    lines between each label on the plot.
    """
    if ax is None:
        ax = plt.gca()

    label_list = [key[0], ]
    for idx, label in enumerate(key[1:]):
        if label != key[idx]:
            label_list.append(label)

    bounds = [0]
    for i in range(len(key)-1):
        if key[i] != key[i+1]:
            ax.axhline(i+0.5, color='lightgrey', linestyle='dashed', zorder=0)
            bounds.append(i+0.5)
    bounds.append(len(key))

    yticks = [(bounds[i] + bounds[i+1])/2 for i in range(len(bounds)-1)]

    ax.set_yticks(yticks, label_list)

def specshow(spec, **kwargs):
    """Use plt.imshow to plot the provided spectrogram, with the following
    modified default parameters:
    
    origin = 'lower'
    aspect = 'auto'
    cmap = 'jet'
    interpolation = 'none'
    """
    origin = kwargs.pop('origin', 'lower')
    aspect = kwargs.pop('aspect', 'auto')
    cmap = kwargs.pop('cmap', 'jet')
    interpolation = kwargs.pop('interpolation', 'none')
    plt.imshow(
        spec,
        origin=origin, cmap=cmap, aspect=aspect, interpolation=interpolation,
        **kwargs
    )

def use_custom_style(style="speech_commands"):
    """Load a custom style file for matplotlib. Looks for
    {MPL_STYLE_DIR}/{style}.mplstyle
    """
    style_pth = os.path.join(MPL_STYLE_DIR, f'{style}.mplstyle')

    if not os.path.exists(style_pth):
        raise FileNotFoundError(f"Style file not found: {style_pth}")

    plt.style.use(style_pth)

def format_yaxis_kHz():
    """Reformat a y-axis showing frequency to display in kHz.
    """
    # format the y-axis
    yticks = plt.yticks()

    plt.yticks(
        yticks[0],
        [tick / 1000 for tick in yticks[0]],
    )
    plt.ylabel('Frequency (kHz)')
    plt.ylim(1000)

def remove_borders(borders=['top', 'right'], ax=None):
    """ Removes the specified borders of the axes.
    Default borders are top and right.
    """
    if ax is None:
        ax = plt.gca()
    ax.spines[borders].set_visible(False)

def wheres_to_raster(wheres, n_idxs):
    raster = [[] for _ in range(n_idxs)]
    for idx, time in zip(*wheres):
        raster[idx].append(time)
    return raster

def plot_event_label_boundaries(
    events:list, boundary_kwargs:dict={}, text_kwargs:dict={}, ax=None,
):
    """Plots boundaries and labels for events defined by a start time, stop
    time, and label.
    
    Parameters
    ----------
    events: list
        List of events [start_time, stop_time, label] for plotting.
    bound_kwargs: dict
        Keyword arguments for plotting the event boundaries (plt.axvline)
    text_kwargs: dict
        Keyword arguments for plotting the event labels (plt.text)
    """
    # get current axes if None supplied
    if not ax:
        ax = plt.gca()
    # default kwargs for boundaries and text
    _boundary_kwargs = {
        'linestyle': 'dashed',
        'color': 'gray',
        'zorder': 0
    }
    _text_kwargs = {
        'y': 0.01,
        'ha': 'center',
        'bbox': {
            'alpha': 0.8,
            'color': 'white',
            'boxstyle': 'Round4, pad=0.0'
        },
        'transform': ax.get_xaxis_transform()
    }

    # update with supplied args
    _boundary_kwargs.update(boundary_kwargs)
    _text_kwargs.update(text_kwargs)

    xi, xf = ax.get_xlim()
    for start_time, stop_time, label in events:
        if start_time <= xf:
            ax.axvline(start_time, **_boundary_kwargs)
        if stop_time >= xi:
            ax.axvline(stop_time, **_boundary_kwargs)
        if xi <= (start_time + stop_time) / 2 <= xf:
            ax.text(x=(start_time + stop_time) / 2, s=label, **_text_kwargs)

def plot_spike_raster(
    raster:list,
    time_shift=0,
    key:list=[],
    ax=None,
    raster_kwargs:dict={},
    adjust_ylim=True,
):
    """Plot a spike raster using pyplot.eventplot().

    Parameters
    ----------
    raster: list[list[float | int]]
        Nested list containing spike times for each index.
    time_shift: float|int, default = 0
        Amount by which to shift the spikes by before plotting.
        t -> t - time_shift for each spike.
    key: dict, default = {}
        Labelling key for the raster indices. If one is supplied, will plot the
        labels using add_key_ylabel()
    ax: Axes, default = None
        Axes on which to plot the raster. If None supplied, will use plt.gca()
    raster_kwargs: dict, default = {}
        kwargs to be supplied to plt.eventplot() when plotting raster.
    """
    if not ax:
        ax = plt.gca()

    # shift spike times if needed
    if np.abs(time_shift) > 0:
        raster = [
            [t - time_shift for t in raster_row]
            for raster_row in raster
        ]

    if key:
        add_key_ylabel(key=key, ax=ax)

    ax.eventplot(raster, **raster_kwargs)

    if adjust_ylim:
        ax.set_ylim(-0.5, len(raster) - 0.5)

def plot_score_mean_std_v_templates(
    scores:'Database',
    score_type:str,
    errorbar_kw:dict={},
    ax:'plt.Axes|None'=None
):
    """
    Plot the mean values of scores entries, sorted by cond_id property.
    Only works for database items which have a `cond_id` attribute.
    """
    cond_ids = np.array(sorted(set(scores.get_attrs('cond_id'))))

    task_values = [
        scores.get_entries(cond_id=cond_id, label=score_type).values
        for cond_id in cond_ids
    ]

    if ax is None:
        ax = plt.gca()

    ax.errorbar(
        x=cond_ids,
        y=[np.mean(vals) for vals in task_values],
        yerr=[np.std(vals) for vals in task_values],
        **errorbar_kw
    )
