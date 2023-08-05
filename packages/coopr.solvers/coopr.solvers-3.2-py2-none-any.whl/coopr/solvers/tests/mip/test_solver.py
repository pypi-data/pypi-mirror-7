#
# Unit Tests for util/misc
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
#import coopr
import coopr.opt
import coopr.solvers.plugins.solvers
import pyutilib.services
import pyutilib.common
from coopr.core.plugin import alias

old_tempdir = pyutilib.services.TempfileManager.tempdir

class TestSolver2(coopr.opt.OptSolver):

    alias('stest2')

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False


class OptSolverDebug(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()
        pyutilib.services.TempfileManager.tempdir = old_tempdir


    def test_solver_init1(self):
        """
        Verify the processing of 'type', 'name' and 'doc' options
        """
        ans = coopr.opt.SolverFactory("_mock_pico")
        self.assertEqual(type(ans), coopr.solvers.plugins.solvers.PICO.MockPICO)
        self.assertEqual(ans._doc, "pico OptSolver")

        ans = coopr.opt.SolverFactory("_mock_pico", doc="My Doc")
        self.assertEqual(type(ans), coopr.solvers.plugins.solvers.PICO.MockPICO)
        self.assertEqual(ans._doc, "My Doc")

        ans = coopr.opt.SolverFactory("_mock_pico", name="my name")
        self.assertEqual(type(ans), coopr.solvers.plugins.solvers.PICO.MockPICO)
        self.assertEqual(ans._doc, "my name OptSolver (type pico)")

    def test_solver_init2(self):
        """
        Verify that options can be passed in.
        """
        opt = {}
        opt['a'] = 1
        opt['b'] = "two"
        ans = coopr.opt.SolverFactory("_mock_pico", name="solver_init2", options=opt)
        self.assertEqual(ans.options['a'], opt['a'])
        self.assertEqual(ans.options['b'], opt['b'])

    def test_avail(self):
        ans = coopr.opt.SolverFactory("stest2")
        try:
            ans.available()
            self.fail("Expected exception for 'stest2' solver, which is disabled")
        except pyutilib.common.ApplicationError:
            pass



if __name__ == "__main__":
    unittest.main()
