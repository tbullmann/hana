import logging
from itertools import chain

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit


def unique_neurons(pair_dict):
    neuron_set = set(list(chain(*list(pair_dict.keys()))))
    return neuron_set


class ModelFunction():
    """
    Base class for modelling data with an function (given as string) with its parameters constrained by bounds.
    """

    def __init__(self, formula_string = None, bounds_dict=None):
        self.variable_list = list(bounds_dict.keys())
        self.variable_string = ",".join(self.variable_list)
        self.bounds = zip(*bounds_dict.values())
        self.func = eval('lambda x, %s: %s' % (self.variable_string, formula_string))
        logging.info('Fitting y(x, %s) = %s' % (self.variable_string, formula_string))
        logging.info(bounds_dict)
        logging.info(self.variable_list)
        logging.info(self.bounds)

    def fit(self, x, y):
        params, cov = curve_fit(self.func, x, y, bounds=self.bounds)
        self.parameters = dict(zip(self.variable_list, params))
        logging.info(self.parameters)

    def predict(self, x, override=None):
        params = self.parameters.copy()
        if override:
            for key in override.keys():
                params[key] = override[key]
        return self.func(x, **params)


def test_fitting_a_model():
    """
    Testing, especially for the eval lambda statements as well as proper assignment of parameters.
    """
    model = model(formula_string='n * norm.pdf(x, loc, scale)',
                  bounds_dict=dict(n=[0, 11016], loc=[-.5, 2.], scale=[0, 10]))

    x = np.linspace(-1,1,15)
    y = model.func(x,n=1,loc=0,scale=0.2)

    model.fitvalues(x, y)

    xfit = np.linspace(-1,1,100)
    yfit = model.predict(xfit, override=dict(n=2))

    plt.plot(x,y,'x')
    plt.plot(xfit,yfit)
    plt.show()