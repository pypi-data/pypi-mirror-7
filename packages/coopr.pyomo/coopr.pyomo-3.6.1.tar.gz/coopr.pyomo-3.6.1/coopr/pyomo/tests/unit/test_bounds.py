#
# Unit Tests for nontrivial Bounds (_SumExpression, _ProductExpression)
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
from coopr.pyomo import *
from nose.tools import nottest

class Test(unittest.TestCase):

    #Test constraint bounds
    def test_constr_lower(self):
        model = AbstractModel()
        model.A = Param(default=2.0, mutable=True)
        model.B = Param(default=1.5, mutable=True)
        model.C = Param(default=2.5, mutable=True)
        model.X = Var()

        def constr_rule(model):
            return (model.A*(model.B+model.C),model.X)
        model.constr = Constraint(rule=constr_rule)

        instance = model.create()
        self.assertEqual(instance.constr.lower(),8.0)

    def test_constr_upper(self):
        model = AbstractModel()
        model.A = Param(default=2.0, mutable=True)
        model.B = Param(default=1.5, mutable=True)
        model.C = Param(default=2.5, mutable=True)
        model.X = Var()

        def constr_rule(model):
            return (model.X,model.A*(model.B+model.C))
        model.constr = Constraint(rule=constr_rule)

        instance = model.create()

        self.assertEqual(instance.constr.upper(),8.0)

    def test_constr_both(self):
        model = AbstractModel()
        model.A = Param(default=2.0, mutable=True)
        model.B = Param(default=1.5, mutable=True)
        model.C = Param(default=2.5, mutable=True)
        model.X = Var()

        def constr_rule(model):
            return (model.A*(model.B-model.C),model.X,model.A*(model.B+model.C))
        model.constr = Constraint(rule=constr_rule)

        instance = model.create()

        self.assertEqual(instance.constr.lower(),-2.0)
        self.assertEqual(instance.constr.upper(),8.0)


    #Test variable bounds
    #JPW: Disabled until we are convinced that we want to support complex parametric expressions for variable bounds.
    def test_var_bounds(self):
        model = AbstractModel()
        model.A = Param(default=2.0, mutable=True)
        model.B = Param(default=1.5, mutable=True)
        model.C = Param(default=2.5)

        def X_bounds_rule(model):
            return (model.A*(model.B-model.C),model.A*(model.B+model.C))
        model.X = Var(bounds=X_bounds_rule)

        instance = model.create()

        self.assertEqual(instance.X.lb,-2.0)
        self.assertEqual(instance.X.ub,8.0)
   

if __name__ == "__main__":
    unittest.main()

