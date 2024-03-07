from core_elements import Program, Class, ClassBody, Constructor, Function, FunctionBody, Variable, Type
from lexer import Lexer, Token

class Parser:

    def parse(self, lexer: Lexer) -> Program:
        '''
        Program : AccessMod ClassMod ClassDeclaration
        '''
        print("Program START")
        
        access_mod: str = self.parse_access_mod(lexer)
        class_mod: str = self.parse_class_mod(lexer)

        class_declaration: Class = self.parse_class_declaration()
        class_declaration.public = (access_mod and access_mod == 'public')

        if class_mod:
            class_declaration.sealed = (class_mod == 'sealed')
            class_declaration.abstract = (class_mod == 'abstract')
    
    def parse_access_mod(self, lexer: Lexer) -> str:
        '''
        AccessMod : PUBLIC | empty
        '''
        print("Access Modifier check")

        tok: Token = lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.PUBLIC: return None

        lexer.pop_token()
        return tok.content

    def parse_class_mod(self, lexer: Lexer) -> str:
        '''
        ClassMod : SEALED | ABSTRACT | empty
        '''
        print("Class Modifier check")
        tok: Token = lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.PUBLIC: return None

        lexer.pop_token()
        return tok.content

    def parse_class_declaration(self, lexer: Lexer) -> Class:
        '''
        ClassDeclaration : CLASS IDENTIFIER ClassExtension LBRACE ClassBody RBRACE
        '''
        print("Class declaration")
        toks: list[Token] = lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.CLASS:
            print("Class declaration missing 'class'")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.CLASS:
            print("Class declaration missing a name")
            raise Exception()
        
        lexer.pop_tokens(2)
        extension: str = self.parse_class_extension(lexer)

        tok: Token = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            print("Class is missing left brace '{'")
            raise Exception()
        
        body: ClassBody = self.parse_class_body(lexer)

    def parse_class_extension(self, lexer: Lexer) -> str:
        '''
        ClassExtension : EXTENDS IDENTIFIER | empty
        '''
        print("Class Extension check")
        toks: list[Token] = lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.EXTENDS: return None
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER: return None
        
        lexer.pop_tokens(2)
        return toks[1].content

    def parse_class_body(self, lexer: Lexer) -> ClassBody:
        '''
        ClassBody : AccessMod Constructor ClassBody 
                   | AccessMod Declaration ClassBody 
                   | COMMENT
                   | empty
        '''
        print("Class Body")
        tok: Token = lexer.peek_next()
        if tok.type == Token.TokenType.COMMENT: return ClassBody([], [], [], [])
        
        access_mod: str = self.parse_access_mod(lexer)
        tok = lexer.peek_next()
        if tok is None:
            print("End of class body")
            return ClassBody([],[],[],[])

        if tok.type == Token.TokenType.CONSTRUCTOR:
            lexer.pop_token()
            constructor = self.parse_constructor(lexer)
            body: ClassBody = self.parse_class_body(lexer)
            return ClassBody([constructor].extend(body.constructors), body.member_vars, body.functions, body.classes)
        else:
            declaration: Variable | Function | Class = self.parse_declaration(lexer)
            declaration.public = (access_mod == 'public')
            body: ClassBody = self.parse_class_body(lexer)
            if type(declaration) == Variable: return ClassBody(body.constructors, [declaration].extend(body.member_vars), body.functions, body.classes)
            elif type(declaration) == Function: return ClassBody(body.constructors, body.member_vars, [declaration].extend(body.functions), body.classes)
            elif type(declaration) == Class: return ClassBody(body.constructors, body.member_vars, body.functions, [declaration].extend(body.classes))
            else:
                print("End of class body")
                return ClassBody([],[],[],[])

    def parse_constructor(self, lexer: Lexer) -> Constructor:
        '''
        Constructor : LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        print("Class Body")
        tok: Token = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LPAREN:
            print("Constructor missing open parenthesis '(")
            raise Exception()

        params: list[Variable] = self.parse_start_params()

        tok = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Constructor missing close parenthesis ')")
            raise Exception()
        
        tok = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            print("Constructor missing open brace '{")
            raise Exception()
        
        body: FunctionBody = self.parse_function_body()
        
        tok = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            print("Constructor missing open brace '}")
            raise Exception()
        
        return Constructor(None, params, body)

    def parse_declaration(self, lexer: Lexer) -> Class | Function | Variable:
        '''
        Declaration : ClassMod ClassDeclaration
                     | MemberMod MemberDeclaration
        '''
        print("Declaration")
        mod: str = self.parse_class_mod(lexer)
        if not mod is None:
            klass: Class = self.parse_class_declaration(lexer)
            klass.sealed = (mod == 'sealed')
            klass.abstract = (mod == 'abstract')
            return klass

        mod = self.parse_member_mod(lexer)
        if not mod is None:
            member: Variable | Function = self.parse_member_declaration(lexer)
            member.static = (mod == 'static')
            return member
        
        print('Class')
        
    def parse_member_mod(self, lexer: Lexer) -> str:
        '''
        MemberMod : STATIC | empty
        '''
        print("Member Mod check")
        tok: Token = lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.STATIC: return None

        lexer.pop_token()
        return tok.content

    def parse_member_declaration(self, lexer: Lexer) -> Variable | Function:
        '''
        MemberDeclaration : VariableDeclaration
                           | FunctionDeclaration
        '''
        print("Member Declaration")
        var: Variable = self.parse_variable_declaration(lexer)
        if not var is None:
            return var
        
        func: Function = self.parse_function_declaration(lexer)
        if not func is None:
            return func
        
        print('Class missing member variable/function declaration')
        raise Exception()

    def parse_variable_declaration(self, lexer: Lexer) -> Variable:
        '''
        VariableDeclaration : VariableMod TYPE IDENTIFIER SEMICOLON
                             | VariableMod TYPE IDENTIFIER Initialization SEMICOLON
        '''
        print("Variable Declaration")
        varmod: str = self.parse_variable_mod(lexer)
        toks: list[Token] = lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.TYPE:
            print("Variable declaration missing type")
            raise Exception()
        
        var_type: Type = None
        for t, type in Type.__members__.items():
            if toks[0].content == t:
                var_type = type
        if var_type is None:
            print(f"Invalid variable type: {var_type}")
            raise Exception()

        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Variable declaration missing name")
            raise Exception()
        name: str = toks[1].content
        
        lexer.pop_tokens(2)

        init_val = self.parse_initialization()

        tok: Token = lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            print("Variable declaration missing a semicolon ';'")
            raise Exception()

        return Variable(None, None, None, var_type, name, init_val)

    def parse_variable_mod(self, lexer: Lexer) -> str:
        '''
        VariableMod : MUTABLE | empty
        '''
        print("Variable Mod check")
        tok: Token = lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.MUTABLE: return None

        lexer.pop_token()
        return tok.content

    def parse_initialization(self, lexer: Lexer):
        '''
        Initialization : SET Expression
                        | SET NEW TYPE LPAREN StartArgs RPAREN
        '''
        print("Initialization")
        ## TODO: Implement this function
        return None

    def parse_function_mod(self, lexer: Lexer) -> str:
        '''
        FunctionMod : SEALED | ABSTRACT | empty
        '''
        print("Function Mod check")
        tok: Token = lexer.peek_next()
        if tok is None or not (tok.type == Token.TokenType.SEALED or tok.type == Token.TokenType.ABSTRACT): return None

        lexer.pop_token()
        return tok.content

    def parse_function_declaration(self, lexer: Lexer) -> Function:
        '''
        FunctionDeclaration : ABSTRACT TYPE FUNCTION IDENTIFIER LPAREN StartParams RPAREN SEMICOLON
                             | SEALED TYPE FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
                             | TYPE FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        print("Function Declaration")
        mod: str = self.parse_function_mod(lexer)
        
        toks: list[Token] = lexer.peek_tokens(4)
        if toks[0] is None or not toks[0].type == Token.TokenType.TYPE:
            print("Function declaration missing type")
            raise Exception()
        
        ret_type: Type = None
        for t, type in Type.__members__.items():
            if toks[0].content == t:
                ret_type = type
        if ret_type is None:
            print(f"Invalid function return type: {ret_type}")
            raise Exception()

        if toks[1] is None or not toks[1].type == Token.TokenType.FUNCTION:
            print("Function declaration not specified")
            raise Exception()
        if toks[2] is None or not toks[2].type == Token.TokenType.IDENTIFIER:
            print("Function declaration missing name")
            raise Exception()
        name: str = toks[2].content

        if toks[3] is None or not toks[3].type == Token.TokenType.LPAREN:
            print("Function declaration missing open parenthesis '('")
            raise Exception()
        
        params: list[Variable] = self.parse_start_params()
        
        

    def parse_start_params(self, lexer: Lexer) -> list[Variable]:
        '''
        StartParams : Params | empty
        '''
        print("Start Param check")
        ## TODO:  IMPLEMENT LATER
        return []

    def parse_params(self, lexer: Lexer) -> list[Variable]:
        '''
        Params : TYPE IDENTIFIER COMMA Params
                | TYPE IDENTIFIER
        '''
        print("Param")

    def parse_function_body(self, lexer: Lexer) -> FunctionBody:
        '''
        IMPLEMENT LATER
        '''
        return FunctionBody()
    
    def parse_start_args(self, lexer: Lexer): # -> list[Expression]:
        '''
        StartArgs : Args | empty
        '''
        print("Start Args check")

    def parse_args(self, lexer: Lexer): # -> list[Expression]:
        '''
        Args : Arg COMMA Args 
              | Arg
        '''
        print("Args check")

    def parse_arg(self, lexer: Lexer): # -> Expression:
        '''
        Arg : IDENTIFIER | FunctionCall
        '''
        print("Arg")

    def parse_expression(self, lexer: Lexer): # -> Expression:
        '''
        Expression : Expression ADD Expression
                    | Expression SUB Expression
                    | Expression MULT Expression
                    | Expression DIV Expression
                    | Expression MOD Expression
                    | FunctionCall
                    | VAL
        '''
        print("Initialization")

    def parse_function_call(self, lexer: Lexer) :#-> Node:
        '''
        FunctionCall : TYPE DOT FunctionCall
                      | IDENTIFIER DOT FunctionCall 
                      | IDENTIFIER DOT LPAREN StartArgs RPAREN
        '''
        print("FunctionCall check")
        