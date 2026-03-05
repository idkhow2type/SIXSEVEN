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

def S(n):
    return FieldSymbol(n,Fraction)
class TestFieldSymbol(unittest.TestCase):
    def test_numeric_atom_combination_and_coercion(self):
        a = FieldSymbol(1, Fraction)
        b = FieldSymbol(2, Fraction)
        self.assertEqual(a + b, FieldSymbol(3, Fraction))
        self.assertEqual(a * b, FieldSymbol(2, Fraction))
        self.assertEqual(b / a, FieldSymbol(2, Fraction))

        x = FieldSymbol("x", Fraction)
        # numeric atoms sort before string atoms, so result should be (1+x)
        self.assertEqual(str(x + FieldSymbol(1, Fraction)), "(x+1)")
        self.assertEqual(str(FieldSymbol(1, Fraction) + x), "(x+1)")

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
        self.assertEqual(str(neg_x), "(x*-1)")
        self.assertEqual(str(neg_x + x), "0")

        # constructor should accept another FieldSymbol of the same num_type
        self.assertEqual(FieldSymbol(FieldSymbol("x", Fraction), Fraction), x)

        # incompatible num_types should not be operable
        with self.assertRaises(TypeError):
            _ = FieldSymbol(1, Fraction) + FieldSymbol(1, float) # type: ignore


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
        self.assertEqual(str(res), "(x+1)")

    def test_long_numeric_sum(self):
        S0 = FieldSymbol(0, Fraction)
        expr = sum((FieldSymbol(1, Fraction) for _ in range(200)), S0)
        self.assertEqual(expr, FieldSymbol(200, Fraction))

    def test_long_alternating_cancellation(self):
        S0 = FieldSymbol(0, Fraction)
        x = FieldSymbol("x", Fraction)
        terms = []
        for _ in range(75):
            terms.append(FieldSymbol(1, Fraction))
            terms.append(FieldSymbol(-1, Fraction))
            terms.append(x)
            terms.append(FieldSymbol(-1, Fraction) * x)
        expr = sum(terms, S0)
        self.assertEqual(expr, FieldSymbol(0, Fraction))

    def test_repeated_multiplicative_inverse_chain(self):
        one = FieldSymbol(1, Fraction)
        x = FieldSymbol("x", Fraction)
        expr = one
        for _ in range(300):
            expr = expr * x * (x ** FieldSymbol(-1, Fraction))
        self.assertEqual(expr, one)

    def test_deeply_nested_numeric_addition_flattening(self):
        acc = FieldSymbol(0, Fraction)
        for i in range(1, 51):
            acc = acc + (FieldSymbol(i, Fraction) + (FieldSymbol(0, Fraction) + FieldSymbol(0, Fraction)))
        self.assertEqual(acc, FieldSymbol(sum(range(1, 51)), Fraction))

    def test_deeply_nested_numeric_multiplication(self):
        prod = FieldSymbol(1, Fraction)
        for i in range(1, 11):
            prod = prod * (FieldSymbol(i, Fraction) * FieldSymbol(1, Fraction))
        expected = 1
        for i in range(1, 11):
            expected *= i
        self.assertEqual(prod, FieldSymbol(expected, Fraction))

    def test_pow_chain_numeric(self):
        self.assertEqual(FieldSymbol(2, Fraction) ** FieldSymbol(3, Fraction), FieldSymbol(8, Fraction))
        self.assertEqual((FieldSymbol(2, Fraction) ** FieldSymbol(3, Fraction)) ** FieldSymbol(2, Fraction), FieldSymbol(64, Fraction))

    def test_add_assoc_combines_numbers_across_nested(self):
        expr = FieldSymbol(2, Fraction) + (FieldSymbol(1, Fraction) + (FieldSymbol(3, Fraction) + FieldSymbol(4, Fraction)))
        self.assertEqual(expr, FieldSymbol(10, Fraction))

    def test_mul_assoc_combines_numbers_across_nested(self):
        expr = FieldSymbol(2, Fraction) * (FieldSymbol(3, Fraction) * FieldSymbol(5, Fraction))
        self.assertEqual(expr, FieldSymbol(30, Fraction))

    def test_idk(self):
        s=(-S('B')/S('A'))
        self.assertEqual(S('A')*s,-S('B'))

    # Tests for the evaluate method
    def test_evaluate_simple_variable(self):
        """Test evaluating a simple variable with a mapping"""
        x = FieldSymbol("x", Fraction)
        result = x.evaluate({"x": FieldSymbol(5, Fraction)})
        self.assertEqual(result, FieldSymbol(5, Fraction))

    def test_evaluate_simple_variable_with_int(self):
        """Test evaluating a variable with an integer mapping"""
        x = FieldSymbol("x", Fraction)
        result = x.evaluate({"x": 5})
        self.assertEqual(result, FieldSymbol(5, Fraction))

    def test_evaluate_simple_variable_with_fraction(self):
        """Test evaluating a variable with a Fraction mapping"""
        x = FieldSymbol("x", Fraction)
        result = x.evaluate({"x": Fraction(1, 2)})
        self.assertEqual(result, FieldSymbol(Fraction(1, 2), Fraction))

    def test_evaluate_numeric_atom(self):
        """Test evaluating a numeric atom"""
        num = FieldSymbol(42, Fraction)
        result = num.evaluate({})
        self.assertEqual(result, FieldSymbol(42, Fraction))

    def test_evaluate_unmapped_variable(self):
        """Test evaluating a variable not in the mapping returns itself"""
        x = FieldSymbol("x", Fraction)
        result = x.evaluate({"y": 5})
        self.assertEqual(result, x)

    def test_evaluate_addition(self):
        """Test evaluating a simple addition expression"""
        x = FieldSymbol("x", Fraction)
        expr = x + FieldSymbol(3, Fraction)
        result = expr.evaluate({"x": 2})
        self.assertEqual(result, FieldSymbol(5, Fraction))

    def test_evaluate_subtraction(self):
        """Test evaluating a simple subtraction expression"""
        x = FieldSymbol("x", Fraction)
        expr = x - FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 7})
        self.assertEqual(result, FieldSymbol(5, Fraction))

    def test_evaluate_multiplication(self):
        """Test evaluating a simple multiplication expression"""
        x = FieldSymbol("x", Fraction)
        expr = x * FieldSymbol(4, Fraction)
        result = expr.evaluate({"x": 3})
        self.assertEqual(result, FieldSymbol(12, Fraction))

    def test_evaluate_division(self):
        """Test evaluating a simple division expression"""
        x = FieldSymbol("x", Fraction)
        expr = x / FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 6})
        self.assertEqual(result, FieldSymbol(3, Fraction))

    def test_evaluate_power(self):
        """Test evaluating a power expression"""
        x = FieldSymbol("x", Fraction)
        expr = x ** FieldSymbol(3, Fraction)
        result = expr.evaluate({"x": 2})
        self.assertEqual(result, FieldSymbol(8, Fraction))

    def test_evaluate_nested_expression(self):
        """Test evaluating a nested expression"""
        x = FieldSymbol("x", Fraction)
        y = FieldSymbol("y", Fraction)
        expr = (x + y) * FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 1, "y": 2})
        self.assertEqual(result, FieldSymbol(6, Fraction))

    def test_evaluate_deep_nesting(self):
        """Test evaluating a deeply nested expression"""
        x = FieldSymbol("x", Fraction)
        expr = ((x + FieldSymbol(1, Fraction)) * FieldSymbol(2, Fraction)) - FieldSymbol(3, Fraction)
        result = expr.evaluate({"x": 5})
        self.assertEqual(result, FieldSymbol(9, Fraction))

    def test_evaluate_multiple_variables(self):
        """Test evaluating an expression with multiple variables"""
        x = FieldSymbol("x", Fraction)
        y = FieldSymbol("y", Fraction)
        z = FieldSymbol("z", Fraction)
        expr = x + y + z
        result = expr.evaluate({"x": 1, "y": 2, "z": 3})
        self.assertEqual(result, FieldSymbol(6, Fraction))

    def test_evaluate_same_variable_multiple_times(self):
        """Test evaluating an expression where the same variable appears multiple times"""
        x = FieldSymbol("x", Fraction)
        expr = x + x
        result = expr.evaluate({"x": 5})
        self.assertEqual(result, FieldSymbol(10, Fraction))

    def test_evaluate_fraction_arithmetic(self):
        """Test evaluating with Fraction field elements"""
        x = FieldSymbol("x", Fraction)
        expr = x / FieldSymbol(3, Fraction)
        result = expr.evaluate({"x": Fraction(1, 2)})
        self.assertEqual(result, FieldSymbol(Fraction(1, 6), Fraction))

    def test_evaluate_field_symbol_mapping(self):
        """Test using FieldSymbol values in the mapping dict"""
        x = FieldSymbol("x", Fraction)
        y = FieldSymbol("y", Fraction)
        expr = x + FieldSymbol(1, Fraction)
        result = expr.evaluate({"x": y})
        self.assertEqual(result, y + FieldSymbol(1, Fraction))

    def test_evaluate_complex_expression(self):
        """Test evaluating a complex expression"""
        x = FieldSymbol("x", Fraction)
        y = FieldSymbol("y", Fraction)
        expr = (x * y) + (FieldSymbol(2, Fraction) * x) - y
        result = expr.evaluate({"x": 3, "y": 4})
        # (3 * 4) + (2 * 3) - 4 = 12 + 6 - 4 = 14
        self.assertEqual(result, FieldSymbol(14, Fraction))

    def test_evaluate_with_partial_mappings(self):
        """Test evaluating with partial variable mappings (some unmapped)"""
        x = FieldSymbol("x", Fraction)
        y = FieldSymbol("y", Fraction)
        expr = x + y
        result = expr.evaluate({"x": 3})
        expected = FieldSymbol(3, Fraction) + y
        self.assertEqual(result, expected)

    def test_evaluate_power_chain(self):
        """Test evaluating chained power expressions"""
        x = FieldSymbol("x", Fraction)
        expr = (x ** FieldSymbol(2, Fraction)) ** FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 2})
        self.assertEqual(result, FieldSymbol(16, Fraction))

    def test_evaluate_division_chain(self):
        """Test evaluating chained division expressions"""
        x = FieldSymbol("x", Fraction)
        expr = (x / FieldSymbol(2, Fraction)) / FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 8})
        self.assertEqual(result, FieldSymbol(2, Fraction))

    def test_evaluate_subtraction_chain(self):
        """Test evaluating chained subtraction"""
        x = FieldSymbol("x", Fraction)
        expr = x - FieldSymbol(1, Fraction) - FieldSymbol(2, Fraction)
        result = expr.evaluate({"x": 10})
        self.assertEqual(result, FieldSymbol(7, Fraction))

    def test_evaluate_empty_mapping(self):
        """Test evaluating with an empty mapping"""
        x = FieldSymbol("x", Fraction)
        result = x.evaluate({})
        self.assertEqual(result, x)

    def test_evaluate_numeric_only_expression(self):
        """Test evaluating an expression with only numeric values"""
        expr = FieldSymbol(2, Fraction) + FieldSymbol(3, Fraction)
        result = expr.evaluate({})
        self.assertEqual(result, FieldSymbol(5, Fraction))


if __name__ == '__main__':
    unittest.main()