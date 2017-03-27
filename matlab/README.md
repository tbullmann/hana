# Network analysis of high-density microelectrode recordings
## Matlab files

The files are very specific to the "hidens" HDMEA and the (internal) cmosmea.git repository of functions to read raw data from `*.ntk` files. 

_NOTE_: In future export all '*.ntk' to '*.h5' and rewrite MATLAB scripts in Phthon: 

* Event extraction
* _Activity maps (from block scan)_
* _Footprint (showing spike wave form)_
* Event cut 
* Spike Sorting (EM Algorithm for Gaussian mixture model)
* Spike triggered averaging (mean, median)
* Movies

Preferably using the [neo](https://pythonhosted.org/neo/) data format which can be found [on Github](https://github.com/NeuralEnsemble/python-neo). 
Support for parallel processing or multiprocessing would be preferably as well. 


### Processing ntk files

* [hidens_extract](hidens_extract.m) (main function to make `*events.mat` and movies) 

### Export

* [export_neurons.m](export_neurons.m) (Export `*event.mat` to `neuron*.h5`, `events.h5`)


