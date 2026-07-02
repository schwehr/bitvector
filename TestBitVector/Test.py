#!/usr/bin/env python

import os
import unittest

import TestBooleanLogic
import TestCircularShifts
import TestComparisonOps
import TestConstructors
import TestPermutations


class BitVectorTestCase(unittest.TestCase):
    def testVersion(self):
        pass


testSuites = [unittest.TestLoader().loadTestsFromTestCase(BitVectorTestCase)]

for test_type in [
    TestConstructors,
    TestBooleanLogic,
    TestComparisonOps,
    TestPermutations,
    TestCircularShifts,
]:
    testSuites.append(test_type.getTestSuites())


def getTestDirectory():
    try:
        return os.path.abspath(os.path.dirname(__file__))
    except Exception:
        return "."


os.chdir(getTestDirectory())

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(testSuites))
