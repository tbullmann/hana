# Network analysis of high-density microelectrode recordings
## Matlab files

The files are very specific to the "hidens" HDMEA and the (internal) cmosmea.git repository of functions to read raw data from `*.ntk` files. 

_NOTE_: In future export all '*.ntk' to '*.h5' and rewrite MATLAB scripts in Python: 

* Event extraction
* _Activity maps_ (from block scan)
* _Footprint_ (showing spike wave form)
* Event cut 
* Spike Sorting (Fitting a Gaussian mixture model by an EM Algorithm)
* Spike triggered averaging (mean, median)
* Movies
* _Burst detection_ (Fitting a hidden Markov model)

Maybe using the [neo](https://pythonhosted.org/neo/) data format which can be found [on Github](https://github.com/NeuralEnsemble/python-neo). 
Support for parallel processing or multiprocessing would be preferably as well. 


### Processing ntk files

* [hidens_extract](hidens_extract.m) (main function to make `*events.mat` and movies) 

### Export

* [export_neurons.m](export_neurons.m) (Export `*event.mat` to `neuron*.h5`, `events.h5`)


