import unittest
from math import pi
from main import comp

class TestComp(unittest.TestCase):

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            comp("2", "3")
        with self.assertRaises(TypeError):
            comp([2], 3)
        with self.assertRaises(TypeError):
            comp((2, ), 3)
        with self.assertRaises(TypeError):
            comp(2, set(3))
        with self.assertRaises(TypeError):
            comp({2}, 3)
        

    def test_sqrt_arg_correct(self):
        res = comp(4, -10)
        self.assertEqual(res, 3)

    
    def test_sqrt_arg_correct_borderline(self):
        res = comp(-5, -10)
        self.assertEqual(res, 0)

    
    def test_sqrt_arg_incorrect(self):
        with self.assertRaises(ValueError):
            comp(-10, -50)


    def test_sin_correct_zero(self):
        res = comp(0, 5)
        self.assertEqual(res, 0)

    
    def test_sin_correct_pos(self):
        res = comp(pi / 2, 5)
        self.assertAlmostEqual(res, 1)

    
    def test_sin_correct_neg(self):
        res = comp(-pi, 5)
        self.assertAlmostEqual(res, 0)
    

    def test_sin_borders(self):
        for i in range(100000):
            with self.subTest(i=i):
                res = comp(i, 1000000)
                b = -1 <= res <= 1
                self.assertTrue(b)  
        
        