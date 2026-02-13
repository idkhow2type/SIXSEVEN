import unittest
from lib import Vector, Matrix, dot, to_rref, RowAdd, RowMul, RowSwap, Zmod, Fraction, FieldSymbol, sign, leibniz_term, permute, T


# class TestVector(unittest.TestCase):
#     def test_vector_creation(self):
#         v = Vector(1, 2, 3)
#         self.assertEqual(len(v), 3)
#         self.assertEqual(v[0], 1)
#         self.assertEqual(v[1], 2)
#         self.assertEqual(v[2], 3)

#     def test_vector_addition(self):
#         v1 = Vector(1, 2, 3)
#         v2 = Vector(4, 5, 6)
#         result = v1 + v2
#         self.assertEqual(result, Vector(5, 7, 9))

#     def test_vector_subtraction(self):
#         v1 = Vector(4, 5, 6)
#         v2 = Vector(1, 2, 3)
#         result = v1 - v2
#         self.assertEqual(result, Vector(3, 3, 3))

#     def test_vector_scalar_multiplication(self):
#         v = Vector(1, 2, 3)
#         result = v * 2
#         self.assertEqual(result, Vector(2, 4, 6))

#     def test_dot_product(self):
#         v1 = Vector(1, 2, 3)
#         v2 = Vector(4, 5, 6)
#         result = dot(v1, v2)
#         self.assertEqual(result, 32)  # 1*4 + 2*5 + 3*6 = 32


# class TestMatrix(unittest.TestCase):
#     def test_matrix_creation(self):
#         m = Matrix([1, 2], [3, 4])
#         self.assertEqual(m.rows, 2)
#         self.assertEqual(m.cols, 2)
#         self.assertEqual(m[0, 0], 1)
#         self.assertEqual(m[0, 1], 2)
#         self.assertEqual(m[1, 0], 3)
#         self.assertEqual(m[1, 1], 4)

#     def test_matrix_addition(self):
#         m1 = Matrix([1, 2], [3, 4])
#         m2 = Matrix([5, 6], [7, 8])
#         result = m1 + m2
#         expected = Matrix([6, 8], [10, 12])
#         self.assertEqual(result, expected)

#     def test_matrix_subtraction(self):
#         m1 = Matrix([5, 6], [7, 8])
#         m2 = Matrix([1, 2], [3, 4])
#         result = m1 - m2
#         expected = Matrix([4, 4], [4, 4])
#         self.assertEqual(result, expected)

#     def test_matrix_scalar_multiplication(self):
#         m = Matrix([1, 2], [3, 4])
#         result = m * 2
#         expected = Matrix([2, 4], [6, 8])
#         self.assertEqual(result, expected)

#     def test_matrix_multiplication(self):
#         m1 = Matrix([1, 2], [3, 4])
#         m2 = Matrix([5, 6], [7, 8])
#         result = m1 @ m2
#         expected = Matrix([19, 22], [43, 50])
#         self.assertEqual(result, expected)

#     def test_matrix_transpose(self):
#         m = Matrix([1, 2, 3], [4, 5, 6])
#         result = m ** T
#         expected = Matrix([1, 4], [2, 5], [3, 6])
#         self.assertEqual(result, expected)

#     def test_identity_matrix(self):
#         ident = Matrix.ident(3)
#         expected = Matrix([1, 0, 0], [0, 1, 0], [0, 0, 1])
#         self.assertEqual(ident, expected)

#     def test_matrix_power(self):
#         m = Matrix([1, 2], [0, 1])
#         result = m ** 2
#         expected = Matrix([1, 4], [0, 1])
#         self.assertEqual(result, expected)

#     def test_matrix_power_zero(self):
#         m = Matrix([1, 2], [3, 4])
#         result = m ** 0
#         expected = Matrix.ident(2)
#         self.assertEqual(result, expected)


# class TestGaussianElimination(unittest.TestCase):
#     def test_to_rref_identity(self):
#         m = Matrix([1, 0], [0, 1])
#         result, ops = to_rref(m)
#         self.assertEqual(result, m)
#         self.assertEqual(len(ops), 0)

#     def test_to_rref_simple(self):
#         m = Matrix([1, 2], [3, 4])
#         result, ops = to_rref(m)
#         # This should produce the identity matrix
#         expected = Matrix([1, 0], [0, 1])
#         self.assertEqual(result, expected)


# class TestRowOperations(unittest.TestCase):
#     def test_row_add(self):
#         m = Matrix([1, 2], [3, 4])
#         op = RowAdd(1, 2, 0)  # R1 = R1 + 2*R0
#         result = op.apply(m)
#         expected = Matrix([1, 2], [5, 8])
#         self.assertEqual(result, expected)

#     def test_row_mul(self):
#         m = Matrix([1, 2], [3, 4])
#         op = RowMul(2, 0)  # R0 = 2*R0
#         result = op.apply(m)
#         expected = Matrix([2, 4], [3, 4])
#         self.assertEqual(result, expected)

#     def test_row_swap(self):
#         m = Matrix([1, 2], [3, 4])
#         op = RowSwap(0, 1)  # Swap R0 and R1
#         result = op.apply(m)
#         expected = Matrix([3, 4], [1, 2])
#         self.assertEqual(result, expected)


# class TestNumberSystems(unittest.TestCase):
#     def test_zmod_arithmetic(self):
#         Z5 = Zmod(5)
#         a = Z5(3)
#         b = Z5(4)
#         self.assertEqual(a + b, Z5(2))  # 3 + 4 = 7 ≡ 2 mod 5
#         self.assertEqual(a * b, Z5(2))  # 3 * 4 = 12 ≡ 2 mod 5
#         self.assertEqual(a - b, Z5(4))  # 3 - 4 = -1 ≡ 4 mod 5

#     def test_zmod_division(self):
#         Z7 = Zmod(7)
#         a = Z7(3)
#         b = Z7(5)
#         result = a / b  # 3 * 5^(-1) mod 7
#         self.assertEqual(result * b, a)  # Check that it's the inverse

#     def test_fraction_repr(self):
#         f = Fraction(3, 4)
#         self.assertEqual(str(f), "3/4")
#         f2 = Fraction(6, 4)
#         self.assertEqual(str(f2), "3/2")


# class TestPermutations(unittest.TestCase):
#     def test_sign_even_permutation(self):
#         perm = (0, 1, 2)  # Identity permutation
#         self.assertEqual(sign(perm), 1)

#     def test_sign_odd_permutation(self):
#         perm = (1, 0, 2)  # One swap
#         self.assertEqual(sign(perm), -1)

#     def test_permute_matrix(self):
#         m = Matrix([1, 2, 3], [4, 5, 6], [7, 8, 9])
#         perm = (2, 0, 1)  # Permute columns: col2, col0, col1
#         result = permute(perm, m)
#         expected = Matrix([3, 1, 2], [6, 4, 5], [9, 7, 8])
#         self.assertEqual(result, expected)

#     def test_leibniz_term(self):
#         m = Matrix([1, 2], [3, 4])
#         perm = (0, 1)
#         result = leibniz_term(perm, m)
#         self.assertEqual(result, 1 * 4 - 2 * 3)  # det = ad - bc


class TestFieldSymbol(unittest.TestCase):
    def test_numeric_atom_combination_and_coercion(self):
        a = FieldSymbol(1, Fraction)
        b = FieldSymbol(2, Fraction)
        self.assertEqual(a + b, FieldSymbol(3, Fraction))
        self.assertEqual(a * b, FieldSymbol(2, Fraction))
        self.assertEqual(b / a, FieldSymbol(2, Fraction))

        x = FieldSymbol("x", Fraction)
        # numeric atoms sort before string atoms, so result should be (1+x)
        self.assertEqual(str(x + FieldSymbol(1, Fraction)), "(1+x)")
        self.assertEqual(str(FieldSymbol(1, Fraction) + x), "(1+x)")

    def test_identity_and_zero(self):
        x = FieldSymbol("x", Fraction)
        zero = FieldSymbol(0, Fraction)
        one = FieldSymbol(1, Fraction)

        self.assertEqual(zero + x, x)
        self.assertEqual(x + zero, x)
        self.assertEqual(one * x, x)
        self.assertEqual(x * one, x)
        self.assertEqual(zero * x, zero)
        self.assertEqual(x * zero, zero)

    def test_division_behaviour_and_errors(self):
        x = FieldSymbol("x", Fraction)
        one = FieldSymbol(1, Fraction)
        zero = FieldSymbol(0, Fraction)

        self.assertEqual(x / one, x)
        self.assertEqual(zero / x, zero)
        self.assertEqual(x / x, one)
        self.assertEqual(str(FieldSymbol(3, Fraction) / FieldSymbol(2, Fraction)), "3/2")

        with self.assertRaises(ZeroDivisionError):
            one / zero

        # reverse-division by a zero FieldSymbol should raise ValueError
        with self.assertRaises(ZeroDivisionError):
            Fraction(1) / zero

    def test_negation_and_equality(self):
        x = FieldSymbol("x", Fraction)
        neg_x = -x
        self.assertEqual(str(neg_x), "(-1*x)")
        self.assertEqual(str(neg_x + x), "0")

        # constructor should accept another FieldSymbol of the same num_type
        self.assertEqual(FieldSymbol(FieldSymbol("x", Fraction), Fraction), x)

        # incompatible num_types should not be operable
        with self.assertRaises(TypeError):
            _ = FieldSymbol(1, Fraction) + FieldSymbol(1, float)


    def test_instance__S_factory_and_coercion(self):
        # instance-level constructor factory (_S) should preserve the instance num_type
        a = FieldSymbol(1, Fraction)
        ctor = a._S
        self.assertEqual(ctor(2), FieldSymbol(2, Fraction))
        self.assertIsInstance(ctor("y"), FieldSymbol)

        # operations that coerce plain values should use the instance's num_type
        x = FieldSymbol("x", Fraction)
        res = x + Fraction(1)
        self.assertIsInstance(res, FieldSymbol)
        # numeric atom should be a Fraction(1)
        self.assertEqual(str(res), "(1+x)")


if __name__ == '__main__':
    unittest.main()