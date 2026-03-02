import unittest
import math
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
        
        
    def test_exp_pos(self):
        res = comp(4, 5)
        self.assertEqual(res, math.exp(4))

    
    def test_exp_zero(self):
        res = comp(0, 2)
        self.assertEqual(res, 1)


    def test_exp_neg(self):
        res = comp(-2, 35)
        self.assertEqual(res, math.exp(-2))


    def test_hyper_pos(self):
        res = comp(10, 5)
        self.assertEqual(res, 1 / 3)

    
    def test_hyper_neg(self):
        res = comp(-7, -10)
        self.assertEqual(res, 1 / -14)


    def test_hyper_error(self):
        with self.assertRaises(ZeroDivisionError):
            comp(7, 2)
    

    def test_multiple(self):
        test_cases = [
            (1, 5, math.e),
            (2, 7, math.exp(2)),
            (6, 6, -1),     
            (8, 5, 1),
            (7, 10, 1 / math.exp(7)),              
        ]
        for x, n, expected in test_cases:
            with self.subTest(x=x, n=n):
                self.assertAlmostEqual(comp(x, n), expected)


if __name__ == "__main__":
    unittest.main()