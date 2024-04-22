import os
import json
import matplotlib.pyplot as plt


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
