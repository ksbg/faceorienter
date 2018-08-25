import sys
from unittest import TestSuite, TextTestRunner, makeSuite

from .test_accuracy import TestAccuracy
from .test_faceorienter import TestFaceOrienter
from .test_rest_api import TestRestAPI
from .test_utils import TestUtils

if len(sys.argv) == 1:
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    suite.addTest(makeSuite(TestFaceOrienter))
    suite.addTest(makeSuite(TestRestAPI))
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
else:
    if sys.argv[1] == 'accuracy':
        TestAccuracy.run()
    else:
        exit('Unknown command line argument: %s' % sys.argv[1])
