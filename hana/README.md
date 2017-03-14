# hana: high density micro electrode array recordings analysis

Hana is a Python library for analysing recordings made by high density micro electrode array.

If you use this library in your research, please cite:

> Bullmann T, et al. Network analysis of high-density microelectrode recordings (????) ????

## Disclaimer

The h4dict code was posted by a unknown user [hjpaul](http://codereview.stackexchange.com/users/27783/hpaulj) on stackexchange,
and the original can be found [here](http://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py)


## Requirements

Hana requires Python 2.7 to run, but is compatible to Pyhton 3.5. 
For a full list of dependencies, see the `requirements.txt` file.


## Installation

### Installing hana 

Clone hana source folder 'hdmea' together with example data and publication figures

```bash
$ git clone http://github.com/tbullmann/hdmea
```

### Installing requirements

Although you can install all the requirements yourself, the easiest way is to use [miniconda](http://conda.pydata.org/miniconda.html). 
Once you used the `conda` command to create and activate a virtual environment:
```bash
$ conda create -name YOUR_ENVIROMENT_NAME python=2.7
$ source activate YOUR_ENVIROMENT_NAME
```
you can simply go the source folder and type:
```bash
$ cd hdmea
$ conda install -f requirements.txt
```
