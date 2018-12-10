"""Provide the class that implements the nonstationary utility function."""
from functools import partial

import numpy as np

from copulpy.attribute_check.check_nonstationary import check_attributes_nonstationary
from copulpy.clsMeta import MetaCls


class NonstationaryUtilCls(MetaCls):
    """Manage the nonstationary utility function."""

    def __init__(self, alpha, beta, gamma, discount_factors, y_scale,
                 unrestricted_weights=None, discounting=None):
        """Initialize nonstationary utility function."""
        self.attr = dict()
        self.attr['discount_factors'] = discount_factors
        self.attr['y_scale'] = y_scale
        self.attr['alpha'] = alpha
        self.attr['gamma'] = gamma
        self.attr['beta'] = beta

        # Optional argument: implement exponential discounting or hyperbolic discounting
        if discounting is not None:
            np.testing.assert_equal(discounting in ['exponential', 'hyperbolic'], True)
            if discounting in ['hyperbolic']:
                new_dfx = {t: discount_factors[0] * discount_factors[1] ** t
                           for t in discount_factors.keys()}
            elif discounting in ['exponential']:
                new_dfx = {t: discount_factors[0] ** t
                           for t in discount_factors.keys()}
            self.attr['discount_factors'] = new_dfx

        # Optional argument: nonparametric weight on y_t in the CES function.
        if unrestricted_weights is None:
            # We apply the g() function here so that y_weights can be used identically below
            y_weights = {t: y_scale * d_f ** (gamma - 1)
                         for t, d_f in discount_factors.items()}
            self.attr['y_weights'] = y_weights
        else:
            # Nonparametric weight: no g() function applied in this case.
            self.attr['y_weights'] = unrestricted_weights

        self._check_attributes_nonstationary = partial(check_attributes_nonstationary, self)
        self._check_attributes_nonstationary()

    def evaluate(self, x, y, t=0):
        """Evaluate the flow utility from consumption (x,y) in period t."""
        alpha, beta, gamma, y_weights, discount_factors = \
            self.get_attr('alpha', 'beta', 'gamma', 'y_weights', 'discount_factors')
        # Marginals: power utility
        v_1 = x ** beta
        v_2 = y ** (beta * gamma)

        # CES: aggregate marginals
        rslt = ((v_1 ** alpha) + ((y_weights[t] * v_2) ** alpha)) ** (1.0 / alpha)

        # utility from the perspective of t=0 is discount factor x flow utility.
        rslt = discount_factors[t] * rslt

        return rslt

    # TODO: Check with Thomas how exchange rates and discount functions are calculated.
    # Additional statistics for temporal decisions. In the future, this might be moved to trempy.
    def univariate_discount_factor(self, money, t):
        """Univariate discount factor."""
        beta, discount_factors = self.get_attr('beta', 'discount_factors')
        delta_t = discount_factors[t]

        indiff_amount = money * delta_t ** (-1 / beta)

        # These adjustment mirror Dennis' code which in turn is shadowing Thomas' Stata code
        ud_factor = (indiff_amount / money - 1) * 12 / max(t, 1)
        if ud_factor != 0:
            ud_factor = ud_factor - 0.025

        if ud_factor > 1.5:
            ud_factor = 1.525

        ud_factor = (1.0 / (1 + ud_factor * (t / 12)))

        return ud_factor

    def exchange_rate(self, money, t):
        """Intratemporal exchange rate."""
        beta, gamma, c_other, discount_factors = \
            self.get_attr('beta', 'gamma', 'y_scale', 'discount_factors')
        delta_t = discount_factors[t]

        indiff_amount = ((money ** (1 / gamma)) * c_other ** (-1 / (beta * gamma)) *
                         (delta_t ** ((1 - gamma) / (beta * gamma))))

        # This transformation is done in Dennis code, which in turn shadows Thomas' Stata code.
        ex_rate = indiff_amount / money
        return ex_rate

    def multivariate_discount_factor_sc(self, money, t):
        """Multivariate discounting from self today to charity tomorrow."""
        beta, gamma, c_other, discount_factors = \
            self.get_attr('beta', 'gamma', 'y_scale', 'discount_factors')
        delta_t = discount_factors[t]

        indiff_amount = ((c_other ** (-1 / (beta * gamma))) *
                         (delta_t ** (-1 / beta)) * (money ** (1 / gamma)))

        # This is again mirroring Dennis' code.
        md_sc = (indiff_amount - 3 * (1 + 1.5 * t / 12)) / money

        return md_sc

    def multivariate_discount_factor_cs(self, money, t):
        """Multivariate discounting from charity today to self tomorrow."""
        beta, gamma, c_other, discount_factors = \
            self.get_attr('beta', 'gamma', 'y_scale', 'discount_factors')
        delta_t = discount_factors[t]

        indiff_amount = ((c_other ** (1 / beta)) * (delta_t ** (-1 / beta))) * (money ** gamma)

        # This is again mirroring Dennis' code.
        md_cs = (indiff_amount - (1 + 1.5 * t / 12)) / money
        return md_cs
