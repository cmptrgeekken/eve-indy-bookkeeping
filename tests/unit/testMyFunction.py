import unittest

from functions.myfunction.myFunction import MyFunction, lambda_handler


class MyFunctionTest(unittest.TestCase):

    def setUp(self):
        self.sut = MyFunction()

    def test_lambda(self):
        lambda_handler('event', 'context')
