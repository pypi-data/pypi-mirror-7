"""
Copyright 2013 Steven Diamond

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

import cvxpy.settings as s
from cvxpy.atoms import *
from cvxpy.expressions.constants import Constant, Parameter
from cvxpy.expressions.variables import Variable
from cvxpy.problems.objective import *
from cvxpy.problems.problem import Problem
import cvxpy.interface as intf
from base_test import BaseTest
from cvxopt import matrix
from numpy import linalg as LA
import numpy
import unittest
import math
import sys
from cStringIO import StringIO

class TestProblem(BaseTest):
    """ Unit tests for the expression/expression module. """
    def setUp(self):
        self.a = Variable(name='a')
        self.b = Variable(name='b')
        self.c = Variable(name='c')

        self.x = Variable(2, name='x')
        self.y = Variable(3, name='y')
        self.z = Variable(2, name='z')

        self.A = Variable(2,2,name='A')
        self.B = Variable(2,2,name='B')
        self.C = Variable(3,2,name='C')

    def test_variables(self):
        """Test the variables method.
        """
        p = Problem(Minimize(self.a), [self.a <= self.x, self.b <= self.A + 2])
        vars_ = p.variables()
        self.assertItemsEqual(vars_, [self.a, self.x, self.b, self.A])

    def test_parameters(self):
        """Test the parameters method.
        """
        p1 = Parameter()
        p2 = Parameter(3, sign="negative")
        p3 = Parameter(4, 4, sign="positive")
        p = Problem(Minimize(p1), [self.a + p1 <= p2, self.b <= p3 + p3 + 2])
        params = p.parameters()
        self.assertItemsEqual(params, [p1, p2, p3])

    # Test silencing and enabling solver messages.
    def test_verbose(self):
        # From http://stackoverflow.com/questions/5136611/capture-stdout-from-a-script-in-python
        # setup the environment
        outputs = {True: [], False: []}
        backup = sys.stdout

        # ####
        for verbose in [True, False]:
            for solver in ["ecos", "cvxopt"]:
                sys.stdout = StringIO()     # capture output
                p = Problem(Minimize(self.a), [self.a >= 2])
                p.solve(verbose=verbose, solver=solver)
                p = Problem(Minimize(self.a), [log(self.a) >= 2])
                p.solve(verbose=verbose, solver=solver)
                out = sys.stdout.getvalue() # release output
                outputs[verbose].append(out.upper())
        # ####

        sys.stdout.close()  # close the stream
        sys.stdout = backup # restore original stdout

        for output in outputs[True]:
            assert len(output) > 0
        for output in outputs[False]:
            assert len(output) == 0

    # Test registering other solve methods.
    def test_register_solve(self):
        Problem.register_solve("test",lambda self: 1)
        p = Problem(Minimize(1))
        result = p.solve(method="test")
        self.assertEqual(result, 1)

        def test(self, a, b=2):
            return (a,b)
        Problem.register_solve("test", test)
        p = Problem(Minimize(0))
        result = p.solve(1,b=3,method="test")
        self.assertEqual(result, (1,3))
        result = p.solve(1,method="test")
        self.assertEqual(result, (1,2))
        result = p.solve(1,method="test",b=4)
        self.assertEqual(result, (1,4))

    def test_consistency(self):
        """Test that variables and constraints keep a consistent order.
        """
        import itertools
        num_solves = 4
        vars_lists = []
        ineqs_lists = []
        for k in range(num_solves):
            sum = 0
            constraints = []
            for i in range(100):
                var = Variable(name=str(i))
                sum += var
                constraints.append(var >= i)
            obj = Minimize(sum)
            p = Problem(obj, constraints)
            objective, constr_map, dims = p.canonicalize()
            all_ineq = itertools.chain(constr_map[s.EQ], constr_map[s.INEQ])
            var_info = p._get_var_offsets(objective, all_ineq)
            sorted_vars, var_offsets, x_length = var_info
            vars_lists.append([int(v.name()) for v in sorted_vars])
            ineqs_lists.append(constr_map[s.INEQ])

        # Verify order of variables is consistent.
        for i in range(num_solves):
            self.assertEqual(range(100), vars_lists[i])
        for i in range(num_solves):
            for idx, constr in enumerate(ineqs_lists[i]):
                var = constr.variables()[0]
                self.assertEqual(idx, int(var.name()))

    # Test removing duplicate constraint objects.
    def test_duplicate_constraints(self):
        eq = (self.x == 2)
        le = (self.x <= 2)
        obj = 0
        def test(self):
            objective,constr_map,dims = self.canonicalize()
            return (len(constr_map[s.EQ]),len(constr_map[s.INEQ]))
        Problem.register_solve("test", test)
        p = Problem(Minimize(obj),[eq,eq,le,le])
        result = p.solve(method="test")
        self.assertEqual(result, (1,1))

    # Test the is_dcp method.
    def test_is_dcp(self):
        p = Problem(Minimize(normInf(self.a)))
        self.assertEqual(p.is_dcp(), True)

        p = Problem(Maximize(normInf(self.a)))
        self.assertEqual(p.is_dcp(), False)
        with self.assertRaises(Exception) as cm:
            p.solve()
        self.assertEqual(str(cm.exception), "Problem does not follow DCP rules.")
        p.solve(ignore_dcp=True)

    # Test problems involving variables with the same name.
    def test_variable_name_conflict(self):
        var = Variable(name='a')
        p = Problem(Maximize(self.a + var), [var == 2 + self.a, var <= 3])
        result = p.solve()
        self.assertAlmostEqual(result, 4.0)
        self.assertAlmostEqual(self.a.value, 1)
        self.assertAlmostEqual(var.value, 3)

    # Test scalar LP problems.
    def test_scalar_lp(self):
        p = Problem(Minimize(3*self.a), [self.a >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 6)
        self.assertAlmostEqual(self.a.value, 2)

        p = Problem(Maximize(3*self.a - self.b),
            [self.a <= 2, self.b == self.a, self.b <= 5])
        result = p.solve()
        self.assertAlmostEqual(result, 4.0)
        self.assertAlmostEqual(self.a.value, 2)
        self.assertAlmostEqual(self.b.value, 2)

        # With a constant in the objective.
        p = Problem(Minimize(3*self.a - self.b + 100),
            [self.a >= 2,
             self.b + 5*self.c - 2 == self.a,
             self.b <= 5 + self.c])
        result = p.solve()
        self.assertAlmostEqual(result, 101 + 1.0/6)
        self.assertAlmostEqual(self.a.value, 2)
        self.assertAlmostEqual(self.b.value, 5-1.0/6)
        self.assertAlmostEqual(self.c.value, -1.0/6)

        # Test status and value.
        exp = Maximize(self.a)
        p = Problem(exp, [self.a <= 2])
        result = p.solve(solver=s.ECOS)
        self.assertEqual(result, p.value)
        self.assertEqual(p.status, s.OPTIMAL)
        assert self.a.value is not None
        assert p.constraints[0].dual_value is not None

        # Unbounded problems.
        p = Problem(Maximize(self.a), [self.a >= 2])
        p.solve(solver=s.ECOS)
        self.assertEqual(p.status, s.UNBOUNDED)
        assert numpy.isinf(p.value)
        assert p.value > 0
        assert self.a.value is None
        assert p.constraints[0].dual_value is None

        p = Problem(Minimize(-self.a), [self.a >= 2])
        result = p.solve(solver=s.CVXOPT)
        self.assertEqual(result, p.value)
        self.assertEqual(p.status, s.UNBOUNDED)
        assert numpy.isinf(p.value)
        assert p.value < 0

        # Infeasible problems.
        p = Problem(Maximize(self.a), [self.a >= 2, self.a <= 1])
        self.a.save_value(2)
        p.constraints[0].save_value(2)

        result = p.solve(solver=s.ECOS)
        self.assertEqual(result, p.value)
        self.assertEqual(p.status, s.INFEASIBLE)
        assert numpy.isinf(p.value)
        assert p.value < 0
        assert self.a.value is None
        assert p.constraints[0].dual_value is None

        p = Problem(Minimize(-self.a), [self.a >= 2, self.a <= 1])
        result = p.solve(solver=s.ECOS)
        self.assertEqual(result, p.value)
        self.assertEqual(p.status, s.INFEASIBLE)
        assert numpy.isinf(p.value)
        assert p.value > 0

    # Test vector LP problems.
    def test_vector_lp(self):
        c = matrix([1,2])
        p = Problem(Minimize(c.T*self.x), [self.x >= c])
        result = p.solve()
        self.assertAlmostEqual(result, 5)
        self.assertItemsAlmostEqual(self.x.value, [1,2])

        A = matrix([[3,5],[1,2]])
        I = Constant([[1,0],[0,1]])
        p = Problem(Minimize(c.T*self.x + self.a),
            [A*self.x >= [-1,1],
             4*I*self.z == self.x,
             self.z >= [2,2],
             self.a >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 26, places=3)
        obj = c.T*self.x.value + self.a.value
        self.assertAlmostEqual(obj[0], result)
        self.assertItemsAlmostEqual(self.x.value, [8,8], places=3)
        self.assertItemsAlmostEqual(self.z.value, [2,2], places=3)

    def test_ecos_noineq(self):
        """Test ECOS with no inequality constraints.
        """
        T = matrix(1, (2, 2))
        p = Problem(Minimize(1), [self.A == T])
        result = p.solve(solver=s.ECOS)
        self.assertAlmostEqual(result, 1)
        self.assertItemsAlmostEqual(self.A.value, T)

    # Test matrix LP problems.
    def test_matrix_lp(self):
        T = matrix(1, (2, 2))
        p = Problem(Minimize(1), [self.A == T])
        result = p.solve()
        self.assertAlmostEqual(result, 1)
        self.assertItemsAlmostEqual(self.A.value, T)

        T = matrix(2,(2,3))
        c = matrix([3,4])
        p = Problem(Minimize(1), [self.A >= T*self.C,
            self.A == self.B, self.C == T.T])
        result = p.solve()
        self.assertAlmostEqual(result, 1)
        self.assertItemsAlmostEqual(self.A.value, self.B.value)
        self.assertItemsAlmostEqual(self.C.value, T)
        assert (self.A.value >= T*self.C.value).all()

        # Test variables are dense.
        self.assertEqual(type(self.A.value), p._DENSE_INTF.TARGET_MATRIX)

    # Test variable promotion.
    def test_variable_promotion(self):
        p = Problem(Minimize(self.a), [self.x <= self.a, self.x == [1,2]])
        result = p.solve()
        self.assertAlmostEqual(result, 2)
        self.assertAlmostEqual(self.a.value, 2)

        p = Problem(Minimize(self.a),
            [self.A <= self.a,
             self.A == [[1,2],[3,4]]
             ])
        result = p.solve()
        self.assertAlmostEqual(result, 4)
        self.assertAlmostEqual(self.a.value, 4)

        # Promotion must happen before the multiplication.
        p = Problem(Minimize([[1],[1]]*(self.x + self.a + 1)),
            [self.a + self.x >= [1,2]])
        result = p.solve()
        self.assertAlmostEqual(result, 5)

    # Test parameter promotion.
    def test_parameter_promotion(self):
        a = Parameter()
        exp = [[1,2],[3,4]]*a
        a.value = 2
        assert not (exp.value - 2*numpy.array([[1,2],[3,4]]).T).any()

    # Test problems with normInf
    def test_normInf(self):
        # Constant argument.
        p = Problem(Minimize(normInf(-2)))
        result = p.solve()
        self.assertAlmostEqual(result, 2)

        # Scalar arguments.
        p = Problem(Minimize(normInf(self.a)), [self.a >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 2)
        self.assertAlmostEqual(self.a.value, 2)

        p = Problem(Minimize(3*normInf(self.a + 2*self.b) + self.c),
            [self.a >= 2, self.b <= -1, self.c == 3])
        result = p.solve()
        self.assertAlmostEqual(result, 3)
        self.assertAlmostEqual(self.a.value + 2*self.b.value, 0)
        self.assertAlmostEqual(self.c.value, 3)

        # Maximize
        p = Problem(Maximize(-normInf(self.a)), [self.a <= -2])
        result = p.solve()
        self.assertAlmostEqual(result, -2)
        self.assertAlmostEqual(self.a.value, -2)

        # Vector arguments.
        p = Problem(Minimize(normInf(self.x - self.z) + 5),
            [self.x >= [2,3], self.z <= [-1,-4]])
        result = p.solve()
        self.assertAlmostEqual(result, 12)
        self.assertAlmostEqual(list(self.x.value)[1] - list(self.z.value)[1], 7)

    # Test problems with norm1
    def test_norm1(self):
        # Constant argument.
        p = Problem(Minimize(norm1(-2)))
        result = p.solve()
        self.assertAlmostEqual(result, 2)

        # Scalar arguments.
        p = Problem(Minimize(norm1(self.a)), [self.a <= -2])
        result = p.solve()
        self.assertAlmostEqual(result, 2)
        self.assertAlmostEqual(self.a.value, -2)

        # Maximize
        p = Problem(Maximize(-norm1(self.a)), [self.a <= -2])
        result = p.solve()
        self.assertAlmostEqual(result, -2)
        self.assertAlmostEqual(self.a.value, -2)

        # Vector arguments.
        p = Problem(Minimize(norm1(self.x - self.z) + 5),
            [self.x >= [2,3], self.z <= [-1,-4]])
        result = p.solve()
        self.assertAlmostEqual(result, 15)
        self.assertAlmostEqual(list(self.x.value)[1] - list(self.z.value)[1], 7)

    # Test problems with norm2
    def test_norm2(self):
        # Constant argument.
        p = Problem(Minimize(norm2(-2)))
        result = p.solve()
        self.assertAlmostEqual(result, 2)

        # Scalar arguments.
        p = Problem(Minimize(norm2(self.a)), [self.a <= -2])
        result = p.solve()
        self.assertAlmostEqual(result, 2)
        self.assertAlmostEqual(self.a.value, -2)

        # Maximize
        p = Problem(Maximize(-norm2(self.a)), [self.a <= -2])
        result = p.solve()
        self.assertAlmostEqual(result, -2)
        self.assertAlmostEqual(self.a.value, -2)

        # Vector arguments.
        p = Problem(Minimize(norm2(self.x - self.z) + 5),
            [self.x >= [2,3], self.z <= [-1,-4]])
        result = p.solve()
        self.assertAlmostEqual(result, 12.61577)
        self.assertItemsAlmostEqual(self.x.value, [2,3])
        self.assertItemsAlmostEqual(self.z.value, [-1,-4])

    # Test problems with abs
    def test_abs(self):
        p = Problem(Minimize(sum(abs(self.A))), [-2 >= self.A])
        result = p.solve()
        self.assertAlmostEqual(result, 8)
        self.assertItemsAlmostEqual(self.A.value, [-2,-2,-2,-2])

    # Test problems with quad_form.
    def test_quad_form(self):
        with self.assertRaises(Exception) as cm:
            Problem(Minimize(quad_form(self.x, self.A))).solve()
        self.assertEqual(str(cm.exception), "At least one argument to quad_form must be constant.")

        with self.assertRaises(Exception) as cm:
            Problem(Minimize(quad_form(1, self.A))).solve()
        self.assertEqual(str(cm.exception), "Invalid dimensions for arguments.")

        with self.assertRaises(Exception) as cm:
            Problem(Minimize(quad_form(self.x, [[-1, 0], [0, 9]]))).solve()
        self.assertEqual(str(cm.exception), "P has both positive and negative eigenvalues.")

        P = [[4, 0], [0, 9]]
        p = Problem(Minimize(quad_form(self.x, P)), [self.x >= 1])
        result = p.solve()
        self.assertAlmostEqual(result, 13, places=3)

        c = [1,2]
        p = Problem(Minimize(quad_form(c, self.A)), [self.A >= 1])
        result = p.solve()
        self.assertAlmostEqual(result, 9)

        c = [1,2]
        P = [[4, 0], [0, 9]]
        p = Problem(Minimize(quad_form(c, P)))
        result = p.solve()
        self.assertAlmostEqual(result, 40)

    # Test combining atoms
    def test_mixed_atoms(self):
        p = Problem(Minimize(norm2(5 + norm1(self.z)
                                  + norm1(self.x) +
                                  normInf(self.x - self.z) ) ),
            [self.x >= [2,3], self.z <= [-1,-4], norm2(self.x + self.z) <= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 22)
        self.assertItemsAlmostEqual(self.x.value, [2,3])
        self.assertItemsAlmostEqual(self.z.value, [-1,-4])

    # Test multiplying by constant atoms.
    def test_mult_constant_atoms(self):
        p = Problem(Minimize(norm2([3,4])*self.a), [self.a >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 10)
        self.assertAlmostEqual(self.a.value, 2)

    # Test recovery of dual variables.
    def test_dual_variables(self):
        p = Problem(Minimize( norm1(self.x + self.z) ),
            [self.x >= [2,3],
             [[1,2],[3,4]]*self.z == [-1,-4],
             norm2(self.x + self.z) <= 100])
        result = p.solve()
        self.assertAlmostEqual(result, 4)
        self.assertItemsAlmostEqual(self.x.value, [4,3])
        self.assertItemsAlmostEqual(self.z.value, [-4,1])
        # Dual values
        self.assertItemsAlmostEqual(p.constraints[0].dual_value, [0, 1])
        self.assertItemsAlmostEqual(p.constraints[1].dual_value, [-1, 0.5])
        self.assertAlmostEqual(p.constraints[2].dual_value, 0)

        T = matrix(2,(2,3))
        c = matrix([3,4])
        p = Problem(Minimize(1),
            [self.A >= T*self.C,
             self.A == self.B,
             self.C == T.T])
        result = p.solve()
        # Dual values
        self.assertItemsAlmostEqual(p.constraints[0].dual_value, 4*[0])
        self.assertItemsAlmostEqual(p.constraints[1].dual_value, 4*[0])
        self.assertItemsAlmostEqual(p.constraints[2].dual_value, 6*[0])

    # Test problems with indexing.
    def test_indexing(self):
        # Vector variables
        p = Problem(Maximize(self.x[0,0]), [self.x[0,0] <= 2, self.x[1,0] == 3])
        result = p.solve()
        self.assertAlmostEqual(result, 2)
        self.assertItemsAlmostEqual(self.x, [2,3])

        n = 10
        A = matrix(range(n*n), (n,n))
        x = Variable(n,n)
        p = Problem(Minimize(sum(x)), [x == A])
        result = p.solve()
        answer = n*n*(n*n+1)/2 - n*n
        self.assertAlmostEqual(result, answer)

        # Matrix variables
        import __builtin__
        p = Problem(Maximize( __builtin__.sum(self.A[i,i] + self.A[i,1-i] for i in range(2)) ),
                             [self.A <= [[1,-2],[-3,4]]])
        result = p.solve()
        self.assertAlmostEqual(result, 0)
        self.assertItemsAlmostEqual(self.A.value, [1,-2,-3,4])

        # Indexing arithmetic expressions.
        exp = [[1,2],[3,4]]*self.z + self.x
        p = Problem(Minimize(exp[1,0]), [self.x == self.z, self.z == [1,2]])
        result = p.solve()
        self.assertAlmostEqual(result, 12)
        self.assertItemsAlmostEqual(self.x.value, self.z.value)

    # Test problems with slicing.
    def test_slicing(self):
        p = Problem(Maximize(sum(self.C)), [self.C[1:3,:] <= 2, self.C[0,:] == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 10)
        self.assertItemsAlmostEqual(self.C.value, 2*[1,2,2])

        p = Problem(Maximize(sum(self.C[0:3:2,1])),
            [self.C[1:3,:] <= 2, self.C[0,:] == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 3)
        self.assertItemsAlmostEqual(self.C.value[0:3:2,1], [1,2])

        p = Problem(Maximize(sum( (self.C[0:2,:] + self.A)[:,0:2] )),
            [self.C[1:3,:] <= 2, self.C[0,:] == 1,
             (self.A + self.B)[:,0] == 3, (self.A + self.B)[:,1] == 2,
             self.B == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 12)
        self.assertItemsAlmostEqual(self.C.value[0:2,:], [1,2,1,2])
        self.assertItemsAlmostEqual(self.A.value, [2,2,1,1])

        p = Problem(Maximize( [[3],[4]]*(self.C[0:2,:] + self.A)[:,0] ),
            [self.C[1:3,:] <= 2, self.C[0,:] == 1,
             [[1],[2]]*(self.A + self.B)[:,0] == 3, (self.A + self.B)[:,1] == 2,
             self.B == 1, 3*self.A[:,0] <= 3])
        result = p.solve()
        self.assertAlmostEqual(result, 12)
        self.assertItemsAlmostEqual(self.C.value[0:2,0], [1,2])
        self.assertItemsAlmostEqual(self.A.value, [1,-.5,1,1])

        p = Problem(Minimize(norm2((self.C[0:2,:] + self.A)[:,0] )),
            [self.C[1:3,:] <= 2, self.C[0,:] == 1,
             (self.A + self.B)[:,0] == 3, (self.A + self.B)[:,1] == 2,
             self.B == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 3)
        self.assertItemsAlmostEqual(self.C.value[0:2,0], [1,-2])
        self.assertItemsAlmostEqual(self.A.value, [2,2,1,1])

        # Transpose of slice.
        p = Problem(Maximize(sum(self.C)), [self.C[1:3,:].T <= 2, self.C[0,:].T == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 10)
        self.assertItemsAlmostEqual(self.C.value, 2*[1,2,2])

    # Test the vstack atom.
    def test_vstack(self):
        c = matrix(1, (1,5))
        p = Problem(Minimize(c * vstack(self.x, self.y)),
            [self.x == [1,2],
            self.y == [3,4,5]])
        result = p.solve()
        self.assertAlmostEqual(result, 15)

        c = matrix(1, (1,4))
        p = Problem(Minimize(c * vstack(self.x, self.x)),
            [self.x == [1,2]])
        result = p.solve()
        self.assertAlmostEqual(result, 6)


        c = matrix(1, (2,2))
        p = Problem( Minimize( sum(vstack(self.A, self.C)) ),
            [self.A >= 2*c,
            self.C == -2])
        result = p.solve()
        self.assertAlmostEqual(result, -4)

        c = matrix(1, (1,2))
        p = Problem( Minimize( sum(vstack(c*self.A, c*self.B)) ),
            [self.A >= 2,
            self.B == -2])
        result = p.solve()
        self.assertAlmostEqual(result, 0)

        c = matrix([1,-1])
        p = Problem( Minimize( c.T * vstack(square(self.a), sqrt(self.b))),
            [self.a == 2,
             self.b == 16])
        result = p.solve()
        self.assertAlmostEqual(result, 0)

    # Test variable transpose.
    def test_transpose(self):
        p = Problem(Minimize(sum(self.x)), [self.x.T >= matrix([1,2]).T])
        result = p.solve()
        self.assertAlmostEqual(result, 3)
        self.assertItemsAlmostEqual(self.x.value, [1,2])

        p = Problem(Minimize(sum(self.C)), [matrix([1,1]).T*self.C.T >= matrix([0,1,2]).T])
        result = p.solve()
        value = self.C.value

        constraints = [1*self.C[i,0] + 1*self.C[i,1] >= i for i in range(3)]
        p = Problem(Minimize(sum(self.C)), constraints)
        result2 = p.solve()
        self.assertAlmostEqual(result, result2)
        self.assertItemsAlmostEqual(self.C.value, value)

        p = Problem(Minimize(self.A[0,1] - self.A.T[1,0]),
                    [self.A == [[1,2],[3,4]]])
        result = p.solve()
        self.assertAlmostEqual(result, 0)

        exp = (-self.x).T
        print exp.size
        p = Problem(Minimize(sum(self.x)), [(-self.x).T <= 1])
        result = p.solve()
        self.assertAlmostEqual(result, -2)

        c = matrix([1,-1])
        p = Problem(Minimize(max(c.T, 2, 2 + c.T)[1]))
        result = p.solve()
        self.assertAlmostEqual(result, 2)

        c = matrix([[1,-1,2],[1,-1,2]])
        p = Problem(Minimize(sum(max(c, 2, 2 + c).T[:,0])))
        result = p.solve()
        self.assertAlmostEqual(result, 6)

        c = matrix([[1,-1,2],[1,-1,2]])
        p = Problem(Minimize(sum(square(c.T).T[:,0])))
        result = p.solve()
        self.assertAlmostEqual(result, 6)

        # Slice of transpose.
        p = Problem(Maximize(sum(self.C)), [self.C.T[:,1:3] <= 2, self.C.T[:,0] == 1])
        result = p.solve()
        self.assertAlmostEqual(result, 10)
        self.assertItemsAlmostEqual(self.C.value, 2*[1,2,2])

    # Test multiplication on the left by a non-constant.
    def test_multiplication_on_left(self):
        c = matrix([1,2])
        p = Problem(Minimize(c.T*self.A*c), [self.A >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 18)

        p = Problem(Minimize(self.a*2), [self.a >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 4)

        p = Problem(Minimize(self.x.T*c), [self.x >= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 6)

        p = Problem(Minimize((self.x.T + self.z.T)*c),
            [self.x >= 2, self.z >= 1])
        result = p.solve()
        self.assertAlmostEqual(result, 9)

    # Test redundant constraints in cvxopt.
    def test_redundant_constraints(self):
        obj = Minimize(sum(self.x))
        constraints = [self.x == 2, self.x == 2, self.x.T == 2, self.x[0] == 2]
        p = Problem(obj, constraints)
        result = p.solve(solver=s.CVXOPT)
        self.assertAlmostEqual(result, 4)

        obj = Minimize(sum(square(self.x)))
        constraints = [self.x == self.x]
        p = Problem(obj, constraints)
        result = p.solve(solver=s.CVXOPT)
        self.assertAlmostEqual(result, 0)

    # Test that symmetry is enforced.
    def test_sdp_symmetry(self):
        # TODO should these raise exceptions?
        # with self.assertRaises(Exception) as cm:
        #     lambda_max([[1,2],[3,4]])
        # self.assertEqual(str(cm.exception), "lambda_max called on non-symmetric matrix.")

        # with self.assertRaises(Exception) as cm:
        #     lambda_min([[1,2],[3,4]])
        # self.assertEqual(str(cm.exception), "lambda_min called on non-symmetric matrix.")

        p = Problem(Minimize(lambda_max(self.A)), [self.A >= 2])
        result = p.solve()
        self.assertItemsAlmostEqual(self.A.value, self.A.value.T)

        p = Problem(Minimize(lambda_max(self.A)), [self.A == [[1,2],[3,4]]])
        result = p.solve()
        self.assertEqual(p.status, s.INFEASIBLE)

    # Test SDP
    def test_sdp(self):
        # Ensure sdp constraints enforce transpose.
        obj = Maximize(self.A[1,0] - self.A[0,1])
        p = Problem(obj, [lambda_max(self.A) <= 100,
                          self.A[0,0] == 2,
                          self.A[1,1] == 2,
                          self.A[1,0] == 2])
        result = p.solve()
        self.assertAlmostEqual(result, 0)

    # Test getting values for expressions.
    def test_expression_values(self):
        diff_exp = self.x - self.z
        inf_exp = normInf(diff_exp)
        sum_exp = 5 + norm1(self.z) + norm1(self.x) + inf_exp
        constr_exp = norm2(self.x + self.z)
        obj = norm2(sum_exp)
        p = Problem(Minimize(obj),
            [self.x >= [2,3], self.z <= [-1,-4], constr_exp <= 2])
        result = p.solve()
        self.assertAlmostEqual(result, 22)
        self.assertItemsAlmostEqual(self.x.value, [2,3])
        self.assertItemsAlmostEqual(self.z.value, [-1,-4])
        # Expression values.
        self.assertItemsAlmostEqual(diff_exp.value, self.x.value - self.z.value)
        self.assertAlmostEqual(inf_exp.value,
            LA.norm(self.x.value - self.z.value, numpy.inf))
        self.assertAlmostEqual(sum_exp.value,
            5 + LA.norm(self.z.value, 1) + LA.norm(self.x.value, 1) + \
            LA.norm(self.x.value - self.z.value, numpy.inf))
        self.assertAlmostEqual(constr_exp.value,
            LA.norm(self.x.value + self.z.value, 2))
        self.assertAlmostEqual(obj.value, result)

    def test_mult_by_zero(self):
        """Test multiplication by zero.
        """
        exp = 0*self.a
        self.assertEqual(exp.value, 0)
        obj = Minimize(exp)
        p = Problem(obj)
        result = p.solve()
        self.assertAlmostEqual(result, 0)
