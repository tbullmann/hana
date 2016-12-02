# (C) http://codereview.stackexchange.com/users/27783/hpaulj
# http://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
#
# The original implementation does not accept other items than strings as key, such integers used for neuron indices,
# but this could be helped by adding an automatic conversion.

import numpy as np
import h5py

def save_dict_to_hdf5(dic, filename):
    """
    ....
    """
    with h5py.File(filename, 'w') as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)

def maybe_convert_to_string(key):
    return str(key) if not isinstance(key, basestring) else key

def maybe_convert_to_int(key):
    return int(key) if key.isdigit() else key

def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + maybe_convert_to_string(key)] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + maybe_convert_to_string(key) + '/', item)
        else:
            raise ValueError('Cannot save %s type'%type(item))

def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')

def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[maybe_convert_to_int(key)] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            ans[maybe_convert_to_int(key)] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans

if __name__ == '__main__':

    data = {'1': 'astring',
            'y': np.arange(10),
            'd': {'z': np.ones((2,3)),
                  'b': b'bytestring'}}
    print(data)
    filename = 'test.h5'
    save_dict_to_hdf5(data, filename)
    dd = load_dict_from_hdf5(filename)
    print(dd)
    # should test for bad type