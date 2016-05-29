import os
import glassfrog
import unittest

from flask import url_for, request, json


class GlassfrogTestCase(unittest.TestCase):

    def setUp(self):
        glassfrog.app.config['TESTING'] = True

    # def tearDown(self):

if __name__ == '__main__':
    unittest.main()
