"""
Copyright 2013 Steven Diamond, Eric Chu

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

from elementwise import Elementwise
from cvxpy.expressions.variables import Variable
from cvxpy.constraints.exponential import ExpCone
import cvxpy.utilities as u
import cvxpy.interface as intf
import numpy as np

class exp(Elementwise):
    """Elementwise :math:`e^{x}`.
    """
    def __init__(self, x):
        super(exp, self).__init__(x)

    # Returns the matrix e^x[i, j].
    @Elementwise.numpy_numeric
    def numeric(self, values):
        return np.exp(values[0])

    # Always positive.
    def sign_from_args(self):
        return u.Sign.POSITIVE

    # Default curvature.
    def func_curvature(self):
        return u.Curvature.CONVEX

    def monotonicity(self):
        return [u.monotonicity.INCREASING]

    def graph_implementation(self, arg_objs):
        rows, cols = self.size
        t = Variable(rows, cols)
        constraints = []
        for i in xrange(rows):
            for j in xrange(cols):
                xi = arg_objs[0][i, j]
                x, y, z = Variable(), Variable(), Variable()
                constraints += [ExpCone(x, y, z),
                                x == xi, y == 1, z == t[i, j]]
        return (t, constraints)
