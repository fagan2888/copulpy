"""This module houses the class for the multiattribute utility copula."""
import numpy as np

from copulpy.clsScaledArchimedean import ScaledArchimedeanCls
from copulpy.shared.auxiliary import distribute_copula_spec
from copulpy.config_copulpy import IS_DEBUG
from copulpy.clsMeta import MetaCls


class UtilityCopulaCls(MetaCls):
    """ This class manages all things related to the multiattribute utility copulas."""
    def __init__(self, copula_spec):

        # Distribute specification
        version, x_uniattribute_utility, y_uniattribute_utility, delta, u, generating_function = \
            distribute_copula_spec(copula_spec, 'version',  'x_uniattribute_utility',
            'y_uniattribute_utility', 'delta', 'u', 'generating_function')

        self.attr = dict()
        self.attr['x_uniattribute_utility'] = x_uniattribute_utility
        self.attr['y_uniattribute_utility'] = y_uniattribute_utility

        self.attr['delta'] = delta
        self.attr['u_1'] = u[0]
        self.attr['u_2'] = u[1]

        if version in ['scaled_archimedean']:
            copula = ScaledArchimedeanCls(generating_function, u[0], u[1], delta)
        else:
            raise NotImplementedError
        self.attr['copula'] = copula

        self._check_attributes()

    def evaluate(self, x, y, is_normalized=False):
        """This function evaluates the multiattribute utility function."""
        # Check integrity of class and request
        self._additional_checks('evaluate_in', x, y)
        self._check_attributes()

        # Distribute class attributes
        attr = ['copula', 'x_uniattribute_utility', 'y_uniattribute_utility']
        copula, x_uniattribute_utility, y_uniattribute_utility = self._distribute_attributes(attr)

        # Construct the normalized points of evaluation.
        if not is_normalized:
            v_1, v_2 = 0.0, 0.0
            if x > 0:
                v_1 = x_uniattribute_utility.evaluate(x, True)
            if y > 0:
                v_2 = y_uniattribute_utility.evaluate(y, True)
        else:
            v_1, v_2 = x, y

        # Evaluate multiattribute utility copula
        rslt = copula.evaluate(v_1, v_2)

        # Checks on return value
        self._additional_checks('evaluate_out', rslt)

        return rslt

    def _check_attributes(self):
        """This function checks the attributes of the class."""
        # Distribute class attributes
        u_1, u_2 = self._distribute_attributes(['u_1', 'u_2'])

        for u in [u_1, u_2]:
            np.testing.assert_equal(0 <= u <= 1, True)

    def _additional_checks(self, label, *args):
        """This method performs some additional checks on selected features of the class
        instance."""
        # We only run these tests during debugging as otherwise the performance deteriorates.
        if not IS_DEBUG:
            return

        if label in ['evaluate_in']:
            for var in args:
                np.testing.assert_equal(np.all(var >= 0), True)
        elif label in ['evaluate_out']:
            rslt, = args
            np.testing.assert_equal(np.all(0.0 <= rslt) <= 1.0, True)
            np.testing.assert_equal(np.all(rslt <= 1.0), True)
        else:
            raise NotImplementedError