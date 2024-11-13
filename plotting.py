import os
import json

import numpy as np
import matplotlib.pyplot as plt

from .data import Database

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


def save_figs(file_name, exts=['pdf', 'png'], **kwargs):
    """Save current pyplot figure in multiple file types.
    """
    for ext in exts:
        plt.savefig(os.path.join(FIG_SAVE_DIR, f"{file_name}.{ext}"), **kwargs)


def save_pdf(file_name):
    """Save the current pyplot figure as a pdf.
    """
    plt.savefig(os.path.join(FIG_SAVE_DIR, f"{file_name}.pdf"))


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


def use_custom_style(style="speech_commands"):
    """Load a custom style file for matplotlib.

    Looks for {MPL_STYLE_DIR}/{style}.mplstyle
    """
    style_pth = os.path.join(MPL_STYLE_DIR, f'{style}.mplstyle')

    if not os.path.exists(style_pth):
        raise FileNotFoundError(f"Style file not found: {style_pth}")

    plt.style.use(style_pth)


def wheres_to_raster(wheres, n_idxs):
    raster = [[] for _ in range(n_idxs)]
    for idx, time in zip(*wheres):
        raster[idx].append(time)
    return raster


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


def add_time_label(lbl_x0, lbl_y, lbl_time, rate, transform=None):
    """ Add a black bar labelled with the duration, in ms."""
    if transform is None:
        transform = plt.gcf().transFigure

    x0, x1 = plt.gca().get_xlim()
    # add time annotation
    lbl_x1 = lbl_x0 + (lbl_time / ((x1 - x0) / rate * 1e3))
    plt.plot(
        [lbl_x0, lbl_x1],
        [lbl_y, lbl_y ],
        color="k",
        transform=transform,
        clip_on=False
    )
    plt.text(
        (lbl_x0 + lbl_x1) / 2, lbl_y - 0.01,
        f'{lbl_time} ms',
        horizontalalignment='center',
        verticalalignment='top',
        transform=transform
    )
