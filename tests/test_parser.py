import unittest
from py_compiler.lexer import Lexer
from py_compiler.parser import Parser
from py_compiler.core_elements import *

class TestParser(unittest.TestCase):

    # Test modifier collection
    def test_parse_modifiers(self): 
        parser = Parser(Lexer("public static sealed abstract mut"), suppress_err=True)
        mods = parser.parse_mods()
        self.assertListEqual(mods, ["public", "static", "sealed", "abstract", "mut"])

    # Test typedef collection
    def test_parse_typedefs_single(self):
        parser = Parser(Lexer("<MyClass>"), suppress_err=True)
        typedefs = parser.parse_typedef()
        self.assertListEqual(typedefs, ["MyClass"])

        parser = Parser(Lexer("MyClass>"), suppress_err=True)
        typedefs = parser.parse_typedef()
        self.assertIsNone(typedefs)

        with self.assertRaises(Exception):
            parser = Parser(Lexer("<>"), suppress_err=True)
            typedefs = parser.parse_typedef()

        with self.assertRaises(Exception):
            parser = Parser(Lexer("<MyClass"), suppress_err=True)
            typedefs = parser.parse_typedef()

    # Test multiple typedef collection
    def test_parse_typedefs_multi(self):
        parser = Parser(Lexer("<Class1, Class2, Class3>"), suppress_err=True)
        typedefs = parser.parse_typedef()
        self.assertListEqual(typedefs, ["Class1", "Class2", "Class3"])

        parser = Parser(Lexer("Class1, Class2, Class3>"), suppress_err=True)
        typedefs = parser.parse_typedef()
        self.assertIsNone(typedefs)

        with self.assertRaises(Exception):
            parser = Parser(Lexer("<Class1, Class2 Class3>"), suppress_err=True)
            typedefs = parser.parse_typedef()

        with self.assertRaises(Exception):
            parser = Parser(Lexer("<Class1, Class2, Class3"), suppress_err=True)
            typedefs = parser.parse_typedef()

    # Test class extension
    def test_parse_class_extension(self):
        parser = Parser(Lexer("extends MyClass"), suppress_err=True)
        ext = parser.parse_class_extension()
        self.assertEqual(ext, "MyClass")

        parser = Parser(Lexer("MyClass"), suppress_err=True)
        ext = parser.parse_class_extension()
        self.assertIsNone(ext)

        with self.assertRaises(Exception):
            parser = Parser(Lexer("extends"), suppress_err=True)
            ext = parser.parse_class_extension()

        with self.assertRaises(Exception):
            parser = Parser(Lexer("extends 0abc"), suppress_err=True)
            ext = parser.parse_class_extension()

    # Test function call
    def test_parse_function_call(self):
        parser = Parser(Lexer("somefunction(1, val1)"), suppress_err=True)
        function_call = parser.parse_function_call()

        self.assertEqual(function_call.name, "somefunction")
        self.assertEqual(len(function_call.args), 2)

        self.assertIsInstance(function_call.args[0], Expression)
        self.assertEqual(len(function_call.args[0].values), 1)
        self.assertIsInstance(function_call.args[0].values[0], Value)
        self.assertEqual(function_call.args[0].values[0].val, "1")

        self.assertIsInstance(function_call.args[1], Expression)
        self.assertEqual(len(function_call.args[1].values), 1)
        self.assertIsInstance(function_call.args[1].values[0], MemberAccess)
        self.assertEqual(len(function_call.args[1].values[0].accesses), 1)
        self.assertIsInstance(function_call.args[1].values[0].accesses[0], VariableAccess)
        self.assertEqual(function_call.args[1].values[0].accesses[0].name, "val1")

    # Test constructor call
    def test_parse_constructor_call(self):
        parser = Parser(Lexer("new SomeClass(1, val1)"), suppress_err=True)
        constructor_call = parser.parse_constructor_call()

        self.assertIsNone(constructor_call.typedefs)
        self.assertEqual(constructor_call.name, "SomeClass")
        self.assertEqual(len(constructor_call.args), 2)

        self.assertIsInstance(constructor_call.args[0], Expression)
        self.assertEqual(len(constructor_call.args[0].values), 1)
        self.assertIsInstance(constructor_call.args[0].values[0], Value)
        self.assertEqual(constructor_call.args[0].values[0].val, "1")

        self.assertIsInstance(constructor_call.args[1], Expression)
        self.assertEqual(len(constructor_call.args[1].values), 1)
        self.assertIsInstance(constructor_call.args[1].values[0], MemberAccess)
        self.assertEqual(len(constructor_call.args[1].values[0].accesses), 1)
        self.assertIsInstance(constructor_call.args[1].values[0].accesses[0], VariableAccess)
        self.assertEqual(constructor_call.args[1].values[0].accesses[0].name, "val1")

    # Test member access
    def test_parse_member_access(self):
        # Test variable access
        parser = Parser(Lexer("val1;"), suppress_err=True)
        member_access = parser.parse_member_access()

        self.assertEqual(len(member_access.accesses), 1)
        self.assertIsInstance(member_access.accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[0].name, "val1")

        # Test function call
        parser = Parser(Lexer("somefunction(val1);"), suppress_err=True)
        member_access = parser.parse_member_access()

        self.assertEqual(len(member_access.accesses), 1)
        self.assertIsInstance(member_access.accesses[0], FunctionCall)
        self.assertEqual(member_access.accesses[0].name, "somefunction")
        self.assertEqual(len(member_access.accesses[0].args), 1)

        self.assertIsInstance(member_access.accesses[0].args[0], Expression)
        self.assertEqual(len(member_access.accesses[0].args[0].values), 1)
        self.assertIsInstance(member_access.accesses[0].args[0].values[0], MemberAccess)
        self.assertEqual(len(member_access.accesses[0].args[0].values[0].accesses), 1)
        self.assertIsInstance(member_access.accesses[0].args[0].values[0].accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[0].args[0].values[0].accesses[0].name, "val1")

        # Test constructor call
        parser = Parser(Lexer("new SomeClass(val1);"), suppress_err=True)
        member_access = parser.parse_member_access()

        self.assertEqual(len(member_access.accesses), 1)
        self.assertIsInstance(member_access.accesses[0], ConstructorCall)
        self.assertEqual(member_access.accesses[0].name, "SomeClass")
        self.assertIsNone(member_access.accesses[0].typedefs)
        self.assertEqual(len(member_access.accesses[0].args), 1)

        self.assertIsInstance(member_access.accesses[0].args[0], Expression)
        self.assertEqual(len(member_access.accesses[0].args[0].values), 1)
        self.assertIsInstance(member_access.accesses[0].args[0].values[0], MemberAccess)
        self.assertEqual(len(member_access.accesses[0].args[0].values[0].accesses), 1)
        self.assertIsInstance(member_access.accesses[0].args[0].values[0].accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[0].args[0].values[0].accesses[0].name, "val1")

        # Test chained accesses
        parser = Parser(Lexer("val1.somefunction(val2).new SomeClass(val3).val4;"), suppress_err=True)
        member_access = parser.parse_member_access()

        self.assertEqual(len(member_access.accesses), 4)

        self.assertIsInstance(member_access.accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[0].name, "val1")

        self.assertIsInstance(member_access.accesses[1], FunctionCall)
        self.assertEqual(member_access.accesses[1].name, "somefunction")
        self.assertEqual(len(member_access.accesses[1].args), 1)

        self.assertIsInstance(member_access.accesses[1].args[0], Expression)
        self.assertEqual(len(member_access.accesses[1].args[0].values), 1)
        self.assertIsInstance(member_access.accesses[1].args[0].values[0], MemberAccess)
        self.assertEqual(len(member_access.accesses[1].args[0].values[0].accesses), 1)
        self.assertIsInstance(member_access.accesses[1].args[0].values[0].accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[1].args[0].values[0].accesses[0].name, "val2")

        self.assertIsInstance(member_access.accesses[2], ConstructorCall)
        self.assertEqual(member_access.accesses[2].name, "SomeClass")
        self.assertIsNone(member_access.accesses[2].typedefs)
        self.assertEqual(len(member_access.accesses[2].args), 1)

        self.assertIsInstance(member_access.accesses[2].args[0], Expression)
        self.assertEqual(len(member_access.accesses[2].args[0].values), 1)
        self.assertIsInstance(member_access.accesses[2].args[0].values[0], MemberAccess)
        self.assertEqual(len(member_access.accesses[2].args[0].values[0].accesses), 1)
        self.assertIsInstance(member_access.accesses[2].args[0].values[0].accesses[0], VariableAccess)
        self.assertEqual(member_access.accesses[2].args[0].values[0].accesses[0].name, "val3")

        self.assertIsInstance(member_access.accesses[3], VariableAccess)
        self.assertEqual(member_access.accesses[3].name, "val4")

    # Test arguments
    def test_parse_arguments(self):
        parser = Parser(Lexer("val1, 132, somefunction(), new SomeClass() )"), suppress_err=True)
        args = parser.parse_args()

        # Check arg1
        self.assertIsInstance(args[0], Expression)
        self.assertEqual(len(args[0].values), 1)
        self.assertIsInstance(args[0].values[0], MemberAccess)
        self.assertEqual(len(args[0].values[0].accesses), 1)
        self.assertIsInstance(args[0].values[0].accesses[0], VariableAccess)
        self.assertEqual(args[0].values[0].accesses[0].name, "val1")

        # Check arg2
        self.assertIsInstance(args[1], Expression)
        self.assertEqual(len(args[1].values), 1)
        self.assertIsInstance(args[1].values[0], Value)
        self.assertEqual(args[1].values[0].val, '132')

        # Check arg3
        self.assertIsInstance(args[2], Expression)
        self.assertEqual(len(args[2].values), 1)
        self.assertIsInstance(args[2].values[0], MemberAccess)
        self.assertEqual(len(args[2].values[0].accesses), 1)
        self.assertIsInstance(args[2].values[0].accesses[0], FunctionCall)
        self.assertEqual(args[2].values[0].accesses[0].name, "somefunction")
        self.assertListEqual(args[2].values[0].accesses[0].args, [])

        # Check arg4
        self.assertIsInstance(args[3], Expression)
        self.assertEqual(len(args[3].values), 1)
        self.assertIsInstance(args[3].values[0], MemberAccess)
        self.assertEqual(len(args[3].values[0].accesses), 1)
        self.assertIsInstance(args[3].values[0].accesses[0], ConstructorCall)
        self.assertEqual(args[3].values[0].accesses[0].name, "SomeClass")
        self.assertIsNone(args[3].values[0].accesses[0].typedefs)
        self.assertListEqual(args[3].values[0].accesses[0].args, [])


