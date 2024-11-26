import unittest
from py_compiler.lexer import Lexer
from py_compiler.parser import Parser
from py_compiler.core_elements import *

class TestParser(unittest.TestCase):

    # Test class collection
    def test_parse_class(self):
        parser = Parser(Lexer('''public abstract class MyClass<T> extends ParentClass {
                                    mut u8 a = 5;
                                    f64 z;
                                    constructor(i32 b) {}
                                    void func somefunction() {}
                              }'''), suppress_err=True)
        c = parser.parse_class()
        self.assertEqual(c, Class(["public", "abstract"], "MyClass", ["T"], "ParentClass", ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        )))

    # Test modifier collection
    def test_parse_modifiers(self): 
        parser = Parser(Lexer("public static sealed abstract mut"), suppress_err=True)
        mods = parser.parse_mods()
        self.assertListEqual(mods, ["public", "static", "sealed", "abstract", "mut"])

    # Test class collection
    def test_parse_class_declaration(self):
        # Test no typedef, no extension
        parser = Parser(Lexer('''class MyClass {
                                    mut u8 a = 5;
                                    f64 z;
                                    constructor(i32 b) {}
                                    void func somefunction() {}
                              }'''), suppress_err=True)
        c = parser.parse_class_declaration()
        self.assertEqual(c, Class(None, "MyClass", None, None, ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        )))

        # Test typedef, no extension
        parser = Parser(Lexer('''class MyClass<T> {
                                    mut u8 a = 5;
                                    f64 z;
                                    constructor(i32 b) {}
                                    void func somefunction() {}
                              }'''), suppress_err=True)
        c = parser.parse_class_declaration()
        self.assertEqual(c, Class(None, "MyClass", ["T"], None, ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        )))

        # Test no typedef, extension
        parser = Parser(Lexer('''class MyClass extends ParentClass {
                                    mut u8 a = 5;
                                    f64 z;
                                    constructor(i32 b) {}
                                    void func somefunction() {}
                              }'''), suppress_err=True)
        c = parser.parse_class_declaration()
        self.assertEqual(c, Class(None, "MyClass", None, "ParentClass", ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        )))

        # Test typedef, extension
        parser = Parser(Lexer('''class MyClass<T> extends ParentClass {
                                    mut u8 a = 5;
                                    f64 z;
                                    constructor(i32 b) {}
                                    void func somefunction() {}
                              }'''), suppress_err=True)
        c = parser.parse_class_declaration()
        self.assertEqual(c, Class(None, "MyClass", ["T"], "ParentClass", ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        )))

    # Test typedef collection
    def test_parse_typedefs_single(self):
        # Typedefs single
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

        # Typedefs multiple
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

    # Test class body collection
    def test_parse_class_body(self):
        parser = Parser(Lexer('''
                                mut u8 a = 5;
                                f64 z;
                                constructor(i32 b) {}
                                void func somefunction() {}
                              }'''), suppress_err=True)
        class_body = parser.parse_class_body()
        
        self.assertEqual(class_body, ClassBody(
            [
                Variable(["mut"], "u8", [], "a", -1, Expression([Value("5")])),
                Variable([], "f64", [], "z", -1)
            ],
            [Constructor([], [Parameter("i32", None, "b")], Body([]))],
            [Function([], "somefunction", "void", [], Body([]))],
            []
        ))

    # Test constructor collection
    def test_parse_constructor(self):
        # Try without params
        parser = Parser(Lexer("() {\na += 1;\n}"), suppress_err=True)
        constructor = parser.parse_constructor()

        self.assertEqual(constructor, Constructor(
            None, [], Body([Statement(VariableUpdate(
                    MemberAccess([VariableAccess("a", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
            ))])
        ))

        # Try with params
        parser = Parser(Lexer("(i32 a, f64 b) {\na += 1;\n}"), suppress_err=True)
        constructor = parser.parse_constructor()

        self.assertEqual(constructor, Constructor(
            None, [Parameter("i32", None, "a"), Parameter("f64", None, "b")],
            Body([Statement(VariableUpdate(
                    MemberAccess([VariableAccess("a", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
            ))])
        ))

    # Test function collection
    def test_parse_function_declaration(self):
        # Try standard function
        parser = Parser(Lexer("void func somefunction(i32 a, f64 b) {\na += 1;\n}"), suppress_err=True)
        func = parser.parse_function_declaration()

        self.assertEqual(func, Function(
            None, "somefunction", "void", [Parameter("i32", None, "a"), Parameter("f64", None, "b")],
            Body([Statement(VariableUpdate(
                    MemberAccess([VariableAccess("a", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
            ))])
        ))

        # Try operator override function
        parser = Parser(Lexer("u8 func operator +(u8 a) {\nreturn a;\n}"), suppress_err=True)
        func = parser.parse_function_declaration()        

        self.assertEqual(func, Function(
            None, "operator_ADD", "u8", [Parameter("u8", None, "a")],
            Body([Statement(Return(Expression([MemberAccess([VariableAccess("a", -1)])])))])
        ))

    # Test variable declaration collection
    def test_parse_variable_declaration(self):
        # Try declaration, no initialization
        parser = Parser(Lexer("i32 x;"), suppress_err=True)
        var_declr = parser.parse_variable_declaration()
        self.assertEqual(var_declr, Variable([], "i32", [], "x", -1))

        # Try declaration w/ typedef, no initialization
        parser = Parser(Lexer("array<f64> x;"), suppress_err=True)
        var_declr = parser.parse_variable_declaration()
        self.assertEqual(var_declr, Variable([], "array", ["f64"], "x", -1))

        # Try declaration, initialized
        parser = Parser(Lexer("i32 x = a + b;"), suppress_err=True)
        var_declr = parser.parse_variable_declaration()
        self.assertEqual(var_declr, Variable([], "i32", [], "x", -1, 
            Expression([
                MemberAccess([VariableAccess("a",-1)]),
                MemberAccess([VariableAccess("b",-1)])
            ], [Operation.ADD])
        ))

        # Try declaration w/ typedef, initialized
        parser = Parser(Lexer("valwrapper<f64> x = 1.123;"), suppress_err=True)
        var_declr = parser.parse_variable_declaration()
        self.assertEqual(var_declr, Variable([], "valwrapper", ["f64"], "x", -1, Expression([Value("1.123")])))

    # Test arguments
    def test_parse_arguments(self):
        parser = Parser(Lexer("val1, 132, somefunction(), new SomeClass() )"), suppress_err=True)
        args = parser.parse_args()

        self.assertListEqual(args, [
            Expression([MemberAccess([VariableAccess("val1", -1)])], []),
            Expression([Value("132")], []),
            Expression([MemberAccess([FunctionCall("somefunction", [])])], []),
            Expression([MemberAccess([ConstructorCall("SomeClass", None, [])])], [])
        ])

    # Test expression collection
    def test_parse_expression(self):
        # Test nested expressions
        parser = Parser(Lexer("(5 * a) - b / 7 % (d + ((e + 10) / f));"), suppress_err=True)
        expr = parser.parse_expression()
        self.assertEqual(expr, Expression([
            Expression([
                Value("5"),
                MemberAccess([VariableAccess("a", -1)])
            ], [Operation.MULT]),
            MemberAccess([VariableAccess("b", -1)]),
            Value("7"),
            Expression([
                MemberAccess([VariableAccess("d", -1)]),
                Expression([
                    Expression([
                        MemberAccess([VariableAccess("e", -1)]),
                        Value("10")
                    ], [Operation.ADD]),
                    MemberAccess([VariableAccess("f", -1)])
                ], [Operation.DIV])
            ], [Operation.ADD])
        ], [Operation.SUB, Operation.DIV, Operation.MOD]))

        # Test all operations
        parser = Parser(Lexer("1 + 2 - 3 * 4 / 5 % 6 & 7 | 8 ^ 9 << 10 >> 11;"), suppress_err=True)
        expr = parser.parse_expression()
        self.assertEqual(expr, Expression([
                Value("1"), Value("2"), Value("3"), Value("4"), Value("5"), Value("6"),
                Value("7"), Value("8"), Value("9"), Value("10"), Value("11")
            ], [Operation.ADD, Operation.SUB, Operation.MULT, Operation.DIV, Operation.MOD, 
                Operation.BIT_AND, Operation.BIT_OR, Operation.BIT_XOR, Operation.BIT_LSHIFT, Operation.BIT_RSHIFT])
        )

    # Test member access
    def test_parse_member_access(self):
        # Test variable access
        parser = Parser(Lexer("val1;"), suppress_err=True)
        member_access = parser.parse_member_access()
        self.assertEqual(member_access, MemberAccess([VariableAccess("val1", -1)]))

        # Test function call
        parser = Parser(Lexer("somefunction(val1);"), suppress_err=True)
        member_access = parser.parse_member_access()
        self.assertEqual(member_access, MemberAccess([FunctionCall("somefunction", [Expression([MemberAccess([VariableAccess("val1", -1)])])])]))

        # Test constructor call
        parser = Parser(Lexer("new SomeClass(val1);"), suppress_err=True)
        member_access = parser.parse_member_access()
        self.assertEqual(member_access, MemberAccess([ConstructorCall("SomeClass", None, [Expression([MemberAccess([VariableAccess("val1", -1)])])])]))

        # Test chained accesses
        parser = Parser(Lexer("val1.somefunction(val2).new SomeClass(val3).val4;"), suppress_err=True)
        member_access = parser.parse_member_access()
        self.assertEqual(member_access, MemberAccess([
            VariableAccess("val1", -1),
            FunctionCall("somefunction", [Expression([MemberAccess([VariableAccess("val2", -1)])])]),
            ConstructorCall("SomeClass", None, [Expression([MemberAccess([VariableAccess("val3", -1)])])]),
            VariableAccess("val4", -1)
        ]))

    # Test constructor call
    def test_parse_constructor_call(self):
        parser = Parser(Lexer("new SomeClass(1, val1)"), suppress_err=True)
        constructor_call = parser.parse_constructor_call()
        self.assertEqual(constructor_call, ConstructorCall("SomeClass", None, [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])]))

    # Test function call
    def test_parse_function_call(self):
        parser = Parser(Lexer("somefunction(1, val1)"), suppress_err=True)
        function_call = parser.parse_function_call()
        self.assertEqual(function_call, FunctionCall("somefunction", [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])]))

    # Test body collection
    def test_parse_body(self):
        # Try if statement
        parser = Parser(Lexer('''
                              if (x < 15) x += 1;
                              while (x < 15) x += 1;
                              for (i32 x = 1; x < 15; x *= 2) x += 1;
                              foreach (i32 x in a.b.c) x += 1;
                              switch (x - 30) {
                                case 1:
                                case 2:
                                    z += 1;
                                default:
                                    z -= 1;
                              }
                              somefunction(1, val1);
                              new SomeClass(1, val1);
                              mut i32 x = 5;
                              --x;
                              asm {
                                "mov r10, r11\nadd r10, r12\nmov rax, r10\nret"
                              }
                              break;
                              return x-5;
                              }'''), suppress_err=True)
        body = parser.parse_body()
        self.assertEqual(body, Body([
            Statement(If(
                False,
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                [],
                None,
                -1
            )),
            Statement(While(
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )),
            Statement(For(
                Variable([], "i32", [], "x", -1, Expression([Value("1")])),
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_MULT,
                    Expression([Value("2")]),
                    -1
                ),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )),
            Statement(ForEach(
                Variable([], "i32", [], "x", -1),
                MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )),
            Statement(Switch(
                Expression([MemberAccess([VariableAccess("x", -1)]), Value("30")], [Operation.SUB]),
                [
                    Case(Value("1"), CaseBody([])),
                    Case(Value("2"), 
                        CaseBody([Statement(VariableUpdate(
                            MemberAccess([VariableAccess("z", -1)]),
                            VariableSetOperation.SET_ADD,
                            Expression([Value("1")]),
                            -1
                        ))])
                    ),
                    Case(None,
                        CaseBody([Statement(VariableUpdate(
                            MemberAccess([VariableAccess("z", -1)]),
                            VariableSetOperation.SET_SUB,
                            Expression([Value("1")]),
                            -1
                        ))]))
                ]
            )),
            Statement(MemberAccess([FunctionCall("somefunction", [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])])])),
            Statement(MemberAccess([ConstructorCall("SomeClass", None, [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])])])),
            Statement(Variable(["mut"], "i32", [], "x", -1, Expression([Value("5")]))),
            Statement(VariableUpdate(MemberAccess([VariableAccess("x", -1)]), VariableSetOperation.DEC, None, -1)),
            Statement(Asm("\"mov r10, r11\nadd r10, r12\nmov rax, r10\nret\"")),
            Statement(Break()),
            Statement(Return(Expression([MemberAccess([VariableAccess("x",-1)]), Value("5")], [Operation.SUB])))
        ]))

    # Test statement collection
    def test_parse_statement(self):
        # Try if statement
        parser = Parser(Lexer("if (x < 15) x += 1;;"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(
            If(
                False,
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                [],
                None,
                -1
            )
        ))

        # Try while statement
        parser = Parser(Lexer("while (x < 15) x += 1;;"), suppress_err=True)
        statement = parser.parse_statement()

        self.assertEqual(statement, Statement(
            While(
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )
        ))

        # Try for statement
        parser = Parser(Lexer("for (i32 x = 1; x < 15; x *= 2) x += 1;;"), suppress_err=True)
        statement = parser.parse_statement()

        self.assertEqual(statement, Statement(
            For(
                Variable([], "i32", [], "x", -1, Expression([Value("1")])),
                Conditions([Condition(
                    Expression([MemberAccess([VariableAccess("x", -1)])]),
                    Expression([Value("15")]),
                    ConditionOperation.LT,
                    False
                )], []),
                VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_MULT,
                    Expression([Value("2")]),
                    -1
                ),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )
        ))

        # Try foreach statement
        parser = Parser(Lexer("foreach (i32 x in a.b.c) x += 1;;"), suppress_err=True)
        statement = parser.parse_statement()

        self.assertEqual(statement, Statement(
            ForEach(
                Variable([], "i32", [], "x", -1),
                MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                -1
            )
        ))

        # Try switch statement
        parser = Parser(Lexer("switch (x - 30) {\ncase 1:\ncase 2:\nz += 1;\ndefault:\nz -= 1;\n}"), suppress_err=True)
        switch = parser.parse_statement()

        self.assertEqual(switch, Statement(
            Switch(
                Expression([MemberAccess([VariableAccess("x", -1)]), Value("30")], [Operation.SUB]),
                [
                    Case(Value("1"), CaseBody([])),
                    Case(Value("2"), 
                        CaseBody([Statement(VariableUpdate(
                            MemberAccess([VariableAccess("z", -1)]),
                            VariableSetOperation.SET_ADD,
                            Expression([Value("1")]),
                            -1
                        ))])
                    ),
                    Case(None,
                        CaseBody([Statement(VariableUpdate(
                            MemberAccess([VariableAccess("z", -1)]),
                            VariableSetOperation.SET_SUB,
                            Expression([Value("1")]),
                            -1
                        ))]))
                ]
            )
        ))

        # Try function call statement
        parser = Parser(Lexer("somefunction(1, val1);"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(MemberAccess([FunctionCall("somefunction", [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])])])))

        # Try constructor call statement
        parser = Parser(Lexer("new SomeClass(1, val1);"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(MemberAccess([ConstructorCall("SomeClass", None, [Expression([Value("1")]), Expression([MemberAccess([VariableAccess("val1", -1)])])])])))

        # Try variable declaration statement
        parser = Parser(Lexer("mut i32 x = 5;"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(Variable(["mut"], "i32", [], "x", -1, Expression([Value("5")]))))

        # Try variable update statement
        parser = Parser(Lexer("--x;"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(VariableUpdate(MemberAccess([VariableAccess("x", -1)]), VariableSetOperation.DEC, None, -1)))

        # Try return statement
        parser = Parser(Lexer("return x-5;"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(Return(Expression([MemberAccess([VariableAccess("x",-1)]), Value("5")], [Operation.SUB]))))

        # Try break statement
        parser = Parser(Lexer("break;"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(Break()))

        # Test asm statement
        parser = Parser(Lexer("asm {\"mov r10, r11\nadd r10, r12\nmov rax, r10\nret\"}"), suppress_err=True)
        statement = parser.parse_statement()
        self.assertEqual(statement, Statement(Asm("\"mov r10, r11\nadd r10, r12\nmov rax, r10\nret\"")))

    # Test return collection
    def test_parse_return(self):
        # Try void return
        parser = Parser(Lexer("return;"), suppress_err=True)
        ret = parser.parse_return()
        self.assertEqual(ret, Return(None))

        # Try new class return
        parser = Parser(Lexer("return new SomeClass();"), suppress_err=True)
        ret = parser.parse_return()
        self.assertEqual(ret, Return(Expression([MemberAccess([ConstructorCall("SomeClass", None, [])])])))

    # Test ASM collection
    def test_parse_asm_block(self):
        # Try void return
        parser = Parser(Lexer("asm {\"mov r10, r11\nadd r10, r12\nmov rax, r10\nret\"}"), suppress_err=True)
        asm = parser.parse_asm_block()
        self.assertEqual(asm, Asm("\"mov r10, r11\nadd r10, r12\nmov rax, r10\nret\""))

    # Test if block collection
    def test_parse_if_block(self):
        # Test single if statement
        parser = Parser(Lexer("if (x < 15) x += 1;;"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            False,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            [],
            None,
            -1
        ))

        # Test constexpr if statement
        parser = Parser(Lexer("if constexpr (x < 15) x += 1;;"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            True,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            [],
            None,
            -1
        ))

        # Test single if body block
        parser = Parser(Lexer("if (x < 15) {\nx += 1;\n};"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            False,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Body([Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            ))]),
            [],
            None,
            -1
        ))

        # Test if/else statement
        parser = Parser(Lexer("if (x < 15) x += 1; else {\nx -= 1;\n}"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            False,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            [],
            Body([Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_SUB,
                Expression([Value("1")]),
                -1
            ))]),
            -1
        ))

        # Test if/elif/else statements
        parser = Parser(Lexer("if (x < 15) x += 1; else if (x < 30) x += 2; else if (x < 45) x += 3; else x -= 1;"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            False,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            [
                If(
                    False,
                    Conditions([Condition(
                        Expression([MemberAccess([VariableAccess("x", -1)])]),
                        Expression([Value("30")]),
                        ConditionOperation.LT,
                        False
                    )], []),
                    Statement(VariableUpdate(
                        MemberAccess([VariableAccess("x", -1)]),
                        VariableSetOperation.SET_ADD,
                        Expression([Value("2")]),
                        -1
                    )),
                    [], None, -1
                ),
                If(
                    False,
                    Conditions([Condition(
                        Expression([MemberAccess([VariableAccess("x", -1)])]),
                        Expression([Value("45")]),
                        ConditionOperation.LT,
                        False
                    )], []),
                    Statement(VariableUpdate(
                        MemberAccess([VariableAccess("x", -1)]),
                        VariableSetOperation.SET_ADD,
                        Expression([Value("3")]),
                        -1
                    )),
                    [], None, -1
                )
            ],
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_SUB,
                Expression([Value("1")]),
                -1
            )),
            -1
        ))

        # Test if/elif/else body blocks
        parser = Parser(Lexer("if (x < 15) {\nx += 1;\n} else if (x < 30) {\nx += 2;\n} else if (x < 45) {\nx += 3;\n} else {\nx -= 1;\n}"), suppress_err=True)
        if_block = parser.parse_if_block()

        self.assertEqual(if_block, If(
            False,
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Body([Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            ))]),
            [
                If(
                    False,
                    Conditions([Condition(
                        Expression([MemberAccess([VariableAccess("x", -1)])]),
                        Expression([Value("30")]),
                        ConditionOperation.LT,
                        False
                    )], []),
                    Body([Statement(VariableUpdate(
                        MemberAccess([VariableAccess("x", -1)]),
                        VariableSetOperation.SET_ADD,
                        Expression([Value("2")]),
                        -1
                    ))]),
                    [], None, -1
                ),
                If(
                    False,
                    Conditions([Condition(
                        Expression([MemberAccess([VariableAccess("x", -1)])]),
                        Expression([Value("45")]),
                        ConditionOperation.LT,
                        False
                    )], []),
                    Body([Statement(VariableUpdate(
                        MemberAccess([VariableAccess("x", -1)]),
                        VariableSetOperation.SET_ADD,
                        Expression([Value("3")]),
                        -1
                    ))]),
                    [], None, -1
                )
            ],
            Body([Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_SUB,
                Expression([Value("1")]),
                -1
            ))]),
            -1
        ))

    # Test while block collection
    def test_parse_while_block(self):
        # Test single statement
        parser = Parser(Lexer("while (x < 15) x += 1;;"), suppress_err=True)
        while_block = parser.parse_while_block()

        self.assertEqual(while_block, While(
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            -1
        ))

        # Test single statement
        parser = Parser(Lexer("while (x < 15) {\nx += 1;\nx /= 5;\n}"), suppress_err=True)
        while_block = parser.parse_while_block()

        self.assertEqual(while_block, While(
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            Body([
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_DIV,
                    Expression([Value("5")]),
                    -1
                ))
            ]),
            -1
        ))

    # Test for block collection
    def test_parse_for_block(self):
        # Test single statement
        parser = Parser(Lexer("for (i32 x = 1; x < 15; x *= 2) x += 1;;"), suppress_err=True)
        for_block = parser.parse_for_block()

        self.assertEqual(for_block, For(
            Variable([], "i32", [], "x", -1, Expression([Value("1")])),
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_MULT,
                Expression([Value("2")]),
                -1
            ),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            -1
        ))

        # Test body block
        parser = Parser(Lexer("for (i32 x = 1; x < 15; x *= 2) {\nx += 1;\nx /= 5;\n}"), suppress_err=True)
        for_block = parser.parse_for_block()

        self.assertEqual(for_block, For(
            Variable([], "i32", [], "x", -1, Expression([Value("1")])),
            Conditions([Condition(
                Expression([MemberAccess([VariableAccess("x", -1)])]),
                Expression([Value("15")]),
                ConditionOperation.LT,
                False
            )], []),
            VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_MULT,
                Expression([Value("2")]),
                -1
            ),
            Body([
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_DIV,
                    Expression([Value("5")]),
                    -1
                ))
            ]),
            -1
        ))

    # Test foreach block collection
    def test_parse_foreach_block(self):
        # Test single statement
        parser = Parser(Lexer("foreach (i32 x in a.b.c) x += 1;;"), suppress_err=True)
        foreach = parser.parse_foreach_block()

        self.assertEqual(foreach, ForEach(
            Variable([], "i32", [], "x", -1),
            MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
            Statement(VariableUpdate(
                MemberAccess([VariableAccess("x", -1)]),
                VariableSetOperation.SET_ADD,
                Expression([Value("1")]),
                -1
            )),
            -1
        ))

        # Test body block
        parser = Parser(Lexer("foreach (i32 x in a.b.c) {\nx += 1;\nx /= 5;\n}"), suppress_err=True)
        foreach = parser.parse_foreach_block()

        self.assertEqual(foreach, ForEach(
            Variable([], "i32", [], "x", -1),
            MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
            Body([
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("x", -1)]),
                    VariableSetOperation.SET_DIV,
                    Expression([Value("5")]),
                    -1
                ))
            ]),
            -1
        ))

    # Test switch block collection
    def test_parse_switch_block(self):
        parser = Parser(Lexer("switch (x - 30) {\ncase 1:\ncase 2:\nz += 1;\ndefault:\nz -= 1;\n}"), suppress_err=True)
        switch = parser.parse_switch()

        self.assertEqual(switch, Switch(
            Expression([MemberAccess([VariableAccess("x", -1)]), Value("30")], [Operation.SUB]),
            [
                Case(Value("1"), CaseBody([])),
                Case(Value("2"), 
                     CaseBody([Statement(VariableUpdate(
                        MemberAccess([VariableAccess("z", -1)]),
                        VariableSetOperation.SET_ADD,
                        Expression([Value("1")]),
                        -1
                    ))])
                ),
                Case(None,
                     CaseBody([Statement(VariableUpdate(
                        MemberAccess([VariableAccess("z", -1)]),
                        VariableSetOperation.SET_SUB,
                        Expression([Value("1")]),
                        -1
                    ))]))
            ]
        ))

    # Test case collection
    def test_parse_case(self):
        parser = Parser(Lexer("case a.b.c:\nz += 1;\nbreak;"), suppress_err=True)
        case = parser.parse_case()

        self.assertEqual(case, Case(
            MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
            CaseBody([
                Statement(VariableUpdate(
                    MemberAccess([VariableAccess("z", -1)]),
                    VariableSetOperation.SET_ADD,
                    Expression([Value("1")]),
                    -1
                )),
                Statement(Break())]
            )
        ))

    # Test conditions collection
    def test_parse_conditions(self):
        # Test AND/OR parsing
        parser = Parser(Lexer("a == b && c != d || e < f || g >= h;"), suppress_err=True)
        conditions = parser.parse_conditions()
        self.assertEqual(conditions, Conditions([
            Condition(
                Expression([MemberAccess([VariableAccess("a", -1)])], []),
                Expression([MemberAccess([VariableAccess("b", -1)])], []),
                ConditionOperation.EQ,
                False
            ),
            Condition(
                Expression([MemberAccess([VariableAccess("c", -1)])], []),
                Expression([MemberAccess([VariableAccess("d", -1)])], []),
                ConditionOperation.NEQ,
                False
            ),
            Condition(
                Expression([MemberAccess([VariableAccess("e", -1)])], []),
                Expression([MemberAccess([VariableAccess("f", -1)])], []),
                ConditionOperation.LT,
                False
            ),
            Condition(
                Expression([MemberAccess([VariableAccess("g", -1)])], []),
                Expression([MemberAccess([VariableAccess("h", -1)])], []),
                ConditionOperation.GEQ,
                False
            )], 
            [True, False, False]
        ))

        # Test negation and conditions with depth
        parser = Parser(Lexer("a == b || !(c == d && e == f)"), suppress_err=True)
        conditions = parser.parse_conditions()
        self.assertEqual(conditions, Conditions([
            Condition(
                Expression([MemberAccess([VariableAccess("a", -1)])], []),
                Expression([MemberAccess([VariableAccess("b", -1)])], []),
                ConditionOperation.EQ,
                False
            ),
            Conditions([
                Condition(
                    Expression([MemberAccess([VariableAccess("c", -1)])], []),
                    Expression([MemberAccess([VariableAccess("d", -1)])], []),
                    ConditionOperation.EQ,
                    True
                ),
                Condition(
                    Expression([MemberAccess([VariableAccess("e", -1)])], []),
                    Expression([MemberAccess([VariableAccess("f", -1)])], []),
                    ConditionOperation.EQ,
                    True
                )],
                [True]
            )],
            [False]
        ))

    # Test single condition collection
    def test_parse_condition(self):
        # Test GT parsing
        parser = Parser(Lexer("a + b > c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.GT,
            False))

        # Test GEQ parsing
        parser = Parser(Lexer("a + b >= c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.GEQ,
            False))

        # Test LT parsing
        parser = Parser(Lexer("a + b < c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.LT,
            False))

        # Test LEQ parsing
        parser = Parser(Lexer("a + b <= c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.LEQ,
            False))

        # Test EQ parsing
        parser = Parser(Lexer("a + b == c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.EQ,
            False))

        # Test NEQ parsing
        parser = Parser(Lexer("a + b != c;"), suppress_err=True)
        condition = parser.parse_condition()
        self.assertEqual(condition, Condition(
            Expression([MemberAccess([VariableAccess("a", -1)]), MemberAccess([VariableAccess("b", -1)])], [Operation.ADD]),
            Expression([MemberAccess([VariableAccess("c", -1)])], []),
            ConditionOperation.NEQ,
            False))

    # Test variable update collection
    def test_parse_variable_update(self):
        # Test member access update
        parser = Parser(Lexer("a.b.c += 1;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1), VariableAccess("b", -1), VariableAccess("c", -1)]),
            VariableSetOperation.SET_ADD,
            Expression([Value("1")]),
            -1
        ))

        # Test SET_ADD parsing
        parser = Parser(Lexer("a += b;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.SET_ADD,
            Expression([MemberAccess([VariableAccess("b", -1)])]),
            -1
        ))

        # Test SET_SUB parsing
        parser = Parser(Lexer("a -= b;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.SET_SUB,
            Expression([MemberAccess([VariableAccess("b", -1)])]),
            -1
        ))

        # Test SET_MULT parsing
        parser = Parser(Lexer("a *= b;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.SET_MULT,
            Expression([MemberAccess([VariableAccess("b", -1)])]),
            -1
        ))

        # Test SET_DIV parsing
        parser = Parser(Lexer("a /= b;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.SET_DIV,
            Expression([MemberAccess([VariableAccess("b", -1)])]),
            -1
        ))

        # Test SET_MOD parsing
        parser = Parser(Lexer("a %= b;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.SET_MOD,
            Expression([MemberAccess([VariableAccess("b", -1)])]),
            -1
        ))

        # Test pre-INC parsing
        parser = Parser(Lexer("++a;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.INC,
            None,
            -1
        ))

        # Test post-INC parsing
        parser = Parser(Lexer("a++;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.INC,
            None,
            -1
        ))

        # Test pre-DEC parsing
        parser = Parser(Lexer("--a;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.DEC,
            None,
            -1
        ))

        # Test post-DEC parsing
        parser = Parser(Lexer("a--;"), suppress_err=True)
        update = parser.parse_variable_update()
        self.assertEqual(update, VariableUpdate(
            MemberAccess([VariableAccess("a", -1)]),
            VariableSetOperation.DEC,
            None,
            -1
        ))