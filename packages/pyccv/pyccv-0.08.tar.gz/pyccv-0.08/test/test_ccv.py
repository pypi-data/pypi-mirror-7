# -*- coding: utf-8 -*-
from PIL import Image
import unittest
import pyccv


class TestCcv(unittest.TestCase):
    def test_ccv(self):
        img = Image.open("./test/test.bmp")
        ccv = pyccv.calc_ccv(img, 240, 25)
        print ccv

    def test_reduce_clor(self):
        img = Image.open("./test/test.bmp")
        print pyccv.reduce_color(img, 240).show()


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCcv))
    return suite
