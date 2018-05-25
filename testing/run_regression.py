#!/usr/bin/env python
"""This module is a first take at regression tests."""
import pickle as pkl
import shutil

import numpy as np

from copulpy.tests.test_auxiliary import generate_random_request
from copulpy.clsUtilityCopula import UtilityCopulaCls
from copulpy.config_copulpy import PACKAGE_DIR



if False:

    NUM_TESTS = 1000
    tests = []
    for _ in range(NUM_TESTS):
        x, y, copula_spec = generate_random_request()

        rslt = UtilityCopulaCls(copula_spec).evaluate(x, y)
        tests += [[rslt, x, y, copula_spec]]

    pkl.dump(tests, open('regression_vault.copulpy.pkl', 'wb'))


tests = pkl.load(open(PACKAGE_DIR + '/tests/regression_vault.copulpy.pkl', 'rb'))
for test in tests:
    # TODO: This does not test the normalization step.
    rslt, x, y, copula_spec = test
    copula = UtilityCopulaCls(copula_spec)
    np.testing.assert_equal(copula.evaluate(x, y), rslt)