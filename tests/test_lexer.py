import unittest
from py_compiler.lexer import Lexer, Token

class TestLexerOperation(unittest.TestCase):

    # Test single next
    def test_lexer_next_single(self):
        input_str = "public sealed".strip()
        lexer = Lexer(input_str)

        # Test first token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.PUBLIC)
        self.assertEqual(tok.content, "public")

        # Test second token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SEALED)
        self.assertEqual(tok.content, "sealed")

        # Test no more tokens
        tok = lexer.next_token()
        self.assertIsNone(tok)

    # Test multiple next
    def test_lexer_next_multiple(self):
        input_str = "public sealed abstract".strip()
        lexer = Lexer(input_str)

        # Test 2 tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.PUBLIC)
        self.assertEqual(toks[0].content, "public")
        self.assertEqual(toks[1].type, Token.TokenType.SEALED)
        self.assertEqual(toks[1].content, "sealed")

        # Test next 2 tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.ABSTRACT)
        self.assertEqual(toks[0].content, "abstract")
        self.assertIsNone(toks[1])

    # Test single peek/pop
    def test_lexer_peek_single(self):
        input_str = "public sealed abstract".strip()
        lexer = Lexer(input_str)

        # Test first token
        peek = lexer.peek_next()
        next = lexer.next_token()
        self.assertEqual(peek, next)

        # Test pop second token
        peek = lexer.peek_next()
        lexer.pop_token()
        self.assertEqual(peek.type, Token.TokenType.SEALED)
        self.assertEqual(peek.content, "sealed")

        # Test duplicate peek
        peek = lexer.peek_next()
        peek2 = lexer.peek_next()
        self.assertEqual(peek, peek2)

    # Test multiple peek/pop
    def test_lexer_peek_multiple(self):
        input_str = "public sealed abstract public".strip()
        lexer = Lexer(input_str)

        # Test 2 tokens
        peeks = lexer.peek_tokens(2)
        nexts = lexer.next_tokens(2)
        self.assertListEqual(peeks, nexts)
        self.assertEqual(peeks[0].type, Token.TokenType.PUBLIC)
        self.assertEqual(peeks[0].content, "public")
        self.assertEqual(peeks[1].type, Token.TokenType.SEALED)
        self.assertEqual(peeks[1].content, "sealed")

        # Test next 2 tokens
        peeks = lexer.peek_tokens(2)
        peeks2 = lexer.peek_tokens(2)
        self.assertListEqual(peeks, peeks2)
        self.assertEqual(peeks[0], lexer.peek_next())
        self.assertEqual(peeks[0].type, Token.TokenType.ABSTRACT)
        self.assertEqual(peeks[0].content, "abstract")
        self.assertEqual(peeks[1].type, Token.TokenType.PUBLIC)
        self.assertEqual(peeks[1].content, "public")

        # Test pop multiple
        lexer.pop_tokens(2)
        peek = lexer.peek_next()
        self.assertIsNone(peek)

class TestLexerTokens(unittest.TestCase):

    # Test class modifier tokens
    def test_tokens_class_modifiers(self):
        input_str = "public sealed abstract".strip()
        lexer = Lexer(input_str)

        # Test PUBLIC token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.PUBLIC)
        self.assertEqual(tok.content, "public")

        # Test SEALED token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SEALED)
        self.assertEqual(tok.content, "sealed")

        # Test ABSTRACT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.ABSTRACT)
        self.assertEqual(tok.content, "abstract")

    # Test class definition tokens
    def test_tokens_class_definition(self):
        input_str = "class ChildClass extends ParentClass".strip()
        lexer = Lexer(input_str)

        # Test CLASS token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.CLASS)
        self.assertEqual(tok.content, "class")

        # Test class name token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "ChildClass")

        # Test EXTENDS token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.EXTENDS)
        self.assertEqual(tok.content, "extends")

        # Test parent class name token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "ParentClass")

    # Test variable declaration tokens
    def test_tokens_variable_declaration(self):
        input_str = "static mut Type variable1".strip()
        lexer = Lexer(input_str)

        # Test STATIC token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.STATIC)
        self.assertEqual(tok.content, "static")

        # Test MUTABLE token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.MUTABLE)
        self.assertEqual(tok.content, "mut")

        # Test variable type token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "Type")

        # Test variable name token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "variable1")

    # Test function declaration tokens
    def test_tokens_function_declaration(self):
        input_str = "void func myFunction() {}".strip()
        lexer = Lexer(input_str)

        # Test return type token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "void")

        # Test FUNCTION token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.FUNCTION)
        self.assertEqual(tok.content, "func")

        # Test function name token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "myFunction")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test operator overloading tokens
    def test_tokens_operator_overloading(self):
        input_str = "i32 func operator +() {}".strip()
        lexer = Lexer(input_str)

        # Test return type token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "i32")

        # Test FUNCTION token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.FUNCTION)
        self.assertEqual(tok.content, "func")

        # Test OPERATOR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.OPERATOR)
        self.assertEqual(tok.content, "operator")

        # Test operation token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.ADD)
        self.assertEqual(tok.content, "+")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test constructor declaration tokens
    def test_tokens_constructor_declaration(self):
        input_str = "constructor() {}".strip()
        lexer = Lexer(input_str)

        # Test CONSTRUCTOR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.CONSTRUCTOR)
        self.assertEqual(tok.content, "constructor")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test constructor call tokens
    def test_tokens_constructor_call(self):
        input_str = "new MyClass() {}".strip()
        lexer = Lexer(input_str)

        # Test NEW token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.NEW)
        self.assertEqual(tok.content, "new")

        # Test class name token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "MyClass")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

    # Test value tokens
    def test_tokens_values(self):
        input_str = "0x0 0x01234567 0x89ABCDEF 0x89abcdef 0o0 0o0123456701234567012345 0b0 0b0000000000111111111100000000001111111111000000000011111111110011 0 123456789 0.0 123.456789".strip()
        lexer = Lexer(input_str)

        # Test hex
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0x0")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0x01234567")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0x89ABCDEF")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0x89abcdef")

        # Test octal
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0o0")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0o0123456701234567012345")

        # Test binary
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0b0")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0b0000000000111111111100000000001111111111000000000011111111110011")

        # Test integer
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "123456789")

        # Test float
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0.0")
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "123.456789")

    # Test bad value tokens
    def test_tokens_values_bad(self):
        # Non hex/octal/binary/dec
        with self.assertRaises(Exception):
            Lexer("0z0").next_token()

        # Hex too short
        with self.assertRaises(Exception):
            Lexer("0x").next_token()

        # Hex too long
        with self.assertRaises(Exception):
            Lexer("0xFFFFFFFFFF").next_token()

        # Hex invalid chars
        with self.assertRaises(Exception):
            Lexer("0xwsldjdas").next_token()

        # Octal too short
        with self.assertRaises(Exception):
            Lexer("0o").next_token()

        # Octal too long
        with self.assertRaises(Exception):
            Lexer("0o7777777777777777777777777").next_token()

        # Octal invalid chars
        with self.assertRaises(Exception):
            Lexer("0o012abc").next_token()

        # Binary too short
        with self.assertRaises(Exception):
            Lexer("0b").next_token()

        # Binary too long
        with self.assertRaises(Exception):
            Lexer("0b00000000001111111111000000000011111111110000000000111111111100001111").next_token()

        # Binary invalid chars
        with self.assertRaises(Exception):
            Lexer("0b012345").next_token()

    # Test if tokens
    def test_tokens_if(self):
        input_str = "if () {} else {}".strip()
        lexer = Lexer(input_str)

        # Test IF token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IF)
        self.assertEqual(tok.content, "if")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

        # Test IF token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.ELSE)
        self.assertEqual(tok.content, "else")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test constexpr tokens
    def test_tokens_constexpre(self):
        input_str = "if constexpr () {} else {}".strip()
        lexer = Lexer(input_str)

        # Test IF token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IF)
        self.assertEqual(tok.content, "if")

        # Test CONSTEXPR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.CONSTEXPR)
        self.assertEqual(tok.content, "constexpr")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test while tokens
    def test_tokens_while(self):
        input_str = "while () {}".strip()
        lexer = Lexer(input_str)

        # Test WHILE token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.WHILE)
        self.assertEqual(tok.content, "while")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test for tokens
    def test_tokens_for(self):
        input_str = "for (;;) {}".strip()
        lexer = Lexer(input_str)

        # Test FOR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.FOR)
        self.assertEqual(tok.content, "for")

        # Test LPAREN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LPAREN)
        self.assertEqual(tok.content, "(")

        # Test semicolon tokens
        toks = lexer.next_tokens(2)
        for tok in toks:
            self.assertEqual(tok.type, Token.TokenType.SEMICOLON)
            self.assertEqual(tok.content, ";")

        # Test RPAREN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.RPAREN)
        self.assertEqual(tok.content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test foreach tokens
    def test_tokens_foreach(self):
        input_str = "foreach ( in someList) {}".strip()
        lexer = Lexer(input_str)

        # Test FOREACH token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.FOREACH)
        self.assertEqual(tok.content, "foreach")

        # Test LPAREN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LPAREN)
        self.assertEqual(tok.content, "(")

        # Test IN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IN)
        self.assertEqual(tok.content, "in")

        # Test iterable variable token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "someList")

        # Test RPAREN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.RPAREN)
        self.assertEqual(tok.content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test switch tokens
    def test_tokens_switch(self):
        input_str = "switch () {}".strip()
        lexer = Lexer(input_str)

        # Test SWITCH token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SWITCH)
        self.assertEqual(tok.content, "switch")

        # Test parenthesis tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LPAREN)
        self.assertEqual(toks[0].content, "(")
        self.assertEqual(toks[1].type, Token.TokenType.RPAREN)
        self.assertEqual(toks[1].content, ")")

        # Test brace tokens
        toks = lexer.next_tokens(2)
        self.assertEqual(toks[0].type, Token.TokenType.LBRACE)
        self.assertEqual(toks[0].content, "{")
        self.assertEqual(toks[1].type, Token.TokenType.RBRACE)
        self.assertEqual(toks[1].content, "}")

    # Test case tokens
    def test_tokens_case(self):
        input_str = "case: break default: break".strip()
        lexer = Lexer(input_str)

        # Test CASE token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.CASE)
        self.assertEqual(tok.content, "case")

        # Test COLON token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.COLON)
        self.assertEqual(tok.content, ":")

        # Test BREAK token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BREAK)
        self.assertEqual(tok.content, "break")

         # Test DEFAULT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.DEFAULT)
        self.assertEqual(tok.content, "default")

        # Test COLON token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.COLON)
        self.assertEqual(tok.content, ":")

        # Test BREAK token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BREAK)
        self.assertEqual(tok.content, "break")

    # Test return tokens
    def test_tokens_return(self):
        input_str = "return".strip()
        lexer = Lexer(input_str)

        # Test RETURN token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.RETURN)
        self.assertEqual(tok.content, "return")

    # Test string tokens
    def test_tokens_string(self):
        input_str = "\"This is a String\"".strip()
        lexer = Lexer(input_str)

        # Test string token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.QUOTE)
        self.assertEqual(tok.content, "\"This is a String\"")

    # Test asm tokens
    def test_tokens_asm(self):
        input_str = "asm {\"This is asm content\"}".strip()
        lexer = Lexer(input_str)

        # Test ASM token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.ASM)
        self.assertEqual(tok.content, "asm")

        # Test LBRACE token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LBRACE)
        self.assertEqual(tok.content, "{")

        # Test ASM content token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.QUOTE)
        self.assertEqual(tok.content, "\"This is asm content\"")

        # Test RBRACE token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.RBRACE)
        self.assertEqual(tok.content, "}")

    # Test member access tokens
    def test_tokens_member_access(self):
        input_str = "someClass.someVar".strip()
        lexer = Lexer(input_str)

        # Test class instance token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "someClass")

        # Test DOT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.DOT)
        self.assertEqual(tok.content, ".")

        # Test member variable token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "someVar")

    # Test list tokens
    def test_tokens_list(self):
        input_str = "a, b, c".strip()
        lexer = Lexer(input_str)

        # Test variable instance token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "a")

        # Test COMMA token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.COMMA)
        self.assertEqual(tok.content, ",")

         # Test variable instance token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "b")

        # Test COMMA token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.COMMA)
        self.assertEqual(tok.content, ",")

         # Test variable instance token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "c")

    # Test array access tokens
    def test_tokens_array_access(self):
        input_str = "arr1[0]".strip()
        lexer = Lexer(input_str)

        # Test array instance token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.IDENTIFIER)
        self.assertEqual(tok.content, "arr1")

        # Test LBRACKET token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LBRACKET)
        self.assertEqual(tok.content, "[")

        # Test index value token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.VAL)
        self.assertEqual(tok.content, "0")

        # Test RBRACKET token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.RBRACKET)
        self.assertEqual(tok.content, "]")

    # Test set operator tokens
    def test_tokens_set_operator(self):
        input_str = "= += -= *= /= %= ++ --".strip()
        lexer = Lexer(input_str)

        # Test SET token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET)
        self.assertEqual(tok.content, "=")

        # Test SET_ADD token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET_ADD)
        self.assertEqual(tok.content, "+=")

        # Test SET_SUB token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET_SUB)
        self.assertEqual(tok.content, "-=")

        # Test SET_MULT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET_MULT)
        self.assertEqual(tok.content, "*=")

        # Test SET_DIV token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET_DIV)
        self.assertEqual(tok.content, "/=")

        # Test SET_MOD token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SET_MOD)
        self.assertEqual(tok.content, "%=")

        # Test INC token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.INC)
        self.assertEqual(tok.content, "++")

        # Test DEC token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.DEC)
        self.assertEqual(tok.content, "--")

    # Test boolean operator tokens
    def test_tokens_boolean_operator(self):
        input_str = "== ! && || <= < >= > !=".strip()
        lexer = Lexer(input_str)

        # Test EQ token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.EQ)
        self.assertEqual(tok.content, "==")

        # Test NOT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.NOT)
        self.assertEqual(tok.content, "!")

        # Test AND token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.AND)
        self.assertEqual(tok.content, "&&")

        # Test OR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.OR)
        self.assertEqual(tok.content, "||")

        # Test LEQ token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LEQ)
        self.assertEqual(tok.content, "<=")

        # Test LT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.LT)
        self.assertEqual(tok.content, "<")

        # Test GEQ token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.GEQ)
        self.assertEqual(tok.content, ">=")

        # Test GT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.GT)
        self.assertEqual(tok.content, ">")

        # Test NEQ token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.NEQ)
        self.assertEqual(tok.content, "!=")

    # Test math operator tokens
    def test_tokens_math_operator(self):
        input_str = "+ - * / % & | ^ ~ << >>".strip()
        lexer = Lexer(input_str)

        # Test ADD token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.ADD)
        self.assertEqual(tok.content, "+")

        # Test SUB token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.SUB)
        self.assertEqual(tok.content, "-")

        # Test MULT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.MULT)
        self.assertEqual(tok.content, "*")

        # Test DIV token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.DIV)
        self.assertEqual(tok.content, "/")

        # Test MOD token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.MOD)
        self.assertEqual(tok.content, "%")

        # Test BIT_AND token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_AND)
        self.assertEqual(tok.content, "&")

        # Test BIT_OR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_OR)
        self.assertEqual(tok.content, "|")

        # Test BIT_XOR token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_XOR)
        self.assertEqual(tok.content, "^")

        # Test BIT_NOT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_NOT)
        self.assertEqual(tok.content, "~")

        # Test BIT_LSHIFT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_LSHIFT)
        self.assertEqual(tok.content, "<<")

        # Test BIT_RSHIFT token
        tok = lexer.next_token()
        self.assertEqual(tok.type, Token.TokenType.BIT_RSHIFT)
        self.assertEqual(tok.content, ">>")