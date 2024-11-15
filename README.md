# snntools
Code designed to be used with Spiking Neural Network (SNN) implementations

## Modules
### Data
A simple database implementation.
Uses dataclasses as entries, with the attributes of the dataclass analogous to the 'columns' of a table.
Useful for quick storage of small amounts of data, providing easier access compared to nested dictionaries.

### Plotting
A collection of functions designed to make plotting spike raster information easier.
This also contains some shortcuts for saving matplotlib figures in a specific directory and as multiple file types, as well as for accessing custom mplstyles.

### Spikes
Contains the SpikeData class, providing a convenient way to handle multi-input spike sequences.
Easily converts a spike sequence into raster, binary array, and other formats.

## Setup
Using the plotting shortcuts requires specifying the default locations for saving figures and finding mplstyle files.
These are specified in the file './dir_info.json', containing the entries
'FIG_SAVE_DIR' and 'MPL_STYLE_DIR'.
