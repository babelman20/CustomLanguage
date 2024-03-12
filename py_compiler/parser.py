from core_elements import Program, Class, ClassBody, Constructor, Function, FunctionBody, Variable, Parameter, Expression, Operation, MemberAccess, FunctionCall
from lexer import Lexer, Token

class Parser:

    def __init__(self, lexer: Lexer, debug_mode: bool = False):
        self.lexer: Lexer = lexer
        self.debug_mode: bool = debug_mode

    def parse(self, ) -> Program:
        '''
        Program : Mods ClassDeclaration
        '''
        if self.debug_mode: print("Program START")
        
        mods: list[str] = self.parse_mods()

        class_declaration: Class = self.parse_class_declaration()
        class_declaration.public = ('public' in mods)
        class_declaration.sealed = ('sealed' in mods)
        class_declaration.abstract = ('abstract' in mods)

        return Program(class_declaration)

    def parse_mods(self) -> list[str]:
        '''
        Mods : PUBLIC|empty STATIC|empty SEALED|ABSTRACT|MUTABLE|empty
        '''
        if self.debug_mode: print("Modifier check")
        mods: list[str] = []

        tok: Token = self.lexer.peek_next()
        if tok is None: return mods
        elif tok.type == Token.TokenType.PUBLIC:
            mods.append(tok.content)
            self.lexer.pop_token()
            tok = self.lexer.peek_next()
            if tok is None: return mods

        if tok.type == Token.TokenType.STATIC:
            mods.append(tok.content)
            self.lexer.pop_token()
            tok = self.lexer.peek_next()
            if tok is None: return mods
        elif tok.type == Token.TokenType.PUBLIC:
            if 'public' in mods:
                print("Can't have 2 access modifiers!")
            else:
                print("Can't have access mod after 'static'")
            raise Exception()

        if tok.type == Token.TokenType.SEALED or tok.type == Token.TokenType.ABSTRACT or tok.type == Token.TokenType.MUTABLE:
            mods.append(tok.content)
            self.lexer.pop_token()
        elif tok.type == Token.TokenType.PUBLIC:
            if 'public' in mods:
                print("Can't have 2 access modifiers!")
            else:
                print("Can't have access mod after 'sealed/abstract/mut'")
            raise Exception()
        elif tok.type == Token.TokenType.STATIC:
            if 'public' in mods:
                print("Can't have 2 static modifiers!")
            else:
                print("Can't have static mod after 'sealed/abstract/mut'")
            raise Exception()
            
        return mods

    def parse_class_declaration(self) -> Class:
        '''
        ClassDeclaration : CLASS IDENTIFIER ClassExtension LBRACE ClassBody RBRACE
        '''
        if self.debug_mode: print("Class declaration")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.CLASS:
            print("Class declaration missing 'class'")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Class declaration missing a name")
            raise Exception()
        
        self.lexer.pop_tokens(2)
        extension: str = self.parse_class_extension()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            print("Class is missing left brace '{'")
            raise Exception()
        
        body: ClassBody = self.parse_class_body()
        return Class(None, None, None, toks[1].content, extension, body)

    def parse_class_extension(self) -> str:
        '''
        ClassExtension : EXTENDS IDENTIFIER | empty
        '''
        if self.debug_mode: print("Class Extension check")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.EXTENDS: return None
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER: return None
        
        self.lexer.pop_tokens(2)
        return toks[1].content

    def parse_class_body(self) -> ClassBody:
        '''
        ClassBody : Mods Constructor|ClassDeclaration|FunctionDeclaration|VariableDeclaration ClassBody 
                   | COMMENT ClassBody
                   | empty
        '''
        if self.debug_mode: ("Class Body")

        mods: list[str] = self.parse_mods()

        tok: Token = self.lexer.peek_next()
        if tok is None or tok.type == Token.TokenType.RBRACE:
            if self.debug_mode: print("End of class body")
            return ClassBody([],[],[],[])
        elif tok.type == Token.TokenType.COMMENT: 
            return self.parse_class_body()
        elif tok.type == Token.TokenType.CONSTRUCTOR:
            self.lexer.pop_token()
            member = self.parse_constructor()
            member.public = ('public' in mods)
        elif tok.type == Token.TokenType.CLASS:
            member = self.parse_class_declaration()
            member.public = ('public' in mods)
            member.sealed = ('sealed' in mods)
            member.abstract = ('abstract' in mods)
        elif tok.type == Token.TokenType.IDENTIFIER:
            type_id = tok.content
            self.lexer.pop_token()
            tok = self.lexer.peek_next()
            if tok.type == Token.TokenType.FUNCTION:
                member = self.parse_function_declaration()
                member.return_type = type_id
                member.public = ('public' in mods)
                member.static = ('static' in mods)
                member.sealed = ('sealed' in mods)
                member.abstract = ('abstract' in mods)
            else:
                if tok.content == 'void':
                    print("Variable can't have 'void' type")
                    raise Exception()
                
                member = self.parse_variable_declaration()
                member.type = type_id
                member.public = ('public' in mods)
                member.static = ('static' in mods)
                member.mutable = ('mut' in mods)
        else:
            print("Expected member or comment in class body ...")
            raise Exception()
        
        body: ClassBody = self.parse_class_body()
        if type(member) is Variable:
            body.member_vars.insert(0,member)
        elif type(member) is Constructor:
            body.constructors.insert(0,member)
        elif type(member) is Function:
            body.functions.insert(0,member)
        elif type(member) is Class:
            body.classes.insert(0,member)
        else:
            print(f"Received unhandled class body member type: {type(member)}")
            raise Exception()
        return body

    def parse_constructor(self) -> Constructor:
        '''
        Constructor : LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        if self.debug_mode: print("Class Body")
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LPAREN:
            print("Constructor missing open parenthesis '('")
            raise Exception()

        params: list[Parameter] = self.parse_start_params()
        if params is None:
            print("Constructor parameters missing ...")
            raise Exception()

        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Constructor missing close parenthesis ')'")
            raise Exception()
        
        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            print("Constructor missing open brace '{'")
            raise Exception()
        
        body: FunctionBody = self.parse_function_body()
        if self.debug_mode: print("Complete function body")
        
        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            print("Constructor missing close brace '}'")
            raise Exception()
        
        return Constructor(None, params, body)

    def parse_variable_declaration(self) -> Variable:
        '''
        VariableDeclaration : IDENTIFIER SEMICOLON
                             | IDENTIFIER Initialization SEMICOLON
        '''
        if self.debug_mode: print("Variable Declaration")
        
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.IDENTIFIER:
            print("Variable declaration missing name")
            raise Exception()
        name: str = tok.content

        init_val = self.parse_initialization()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            print("Variable declaration missing a semicolon ';'")
            raise Exception()

        return Variable(None, None, None, None, name, init_val)

    def parse_initialization(self):
        '''
        Initialization : SET Expression
                        | SET NEW IDENTIFIER LPAREN StartArgs RPAREN
        '''
        if self.debug_mode: print("Initialization")
        ## TODO: Implement this function
        return None

    def parse_function_declaration(self) -> Function:
        '''
        FunctionDeclaration : FUNCTION IDENTIFIER LPAREN StartParams RPAREN SEMICOLON
                             | FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
                             | FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        if self.debug_mode: print("Function Declaration")
        
        toks: list[Token] = self.lexer.next_tokens(3)
        if toks[0] is None or not toks[0].type == Token.TokenType.FUNCTION:
            print("Function declaration not specified")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Function declaration missing name")
            raise Exception()
        name: str = toks[1].content

        if toks[2] is None or not toks[2].type == Token.TokenType.LPAREN:
            print("Function declaration missing open parenthesis '('")
            raise Exception()
                
        params: list[Parameter] = self.parse_start_params()
        if params is None:
            print("Function parameters missing ...")
            raise Exception()

        toks = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.RPAREN:
            print("Function parameters missing close parenthesis ')'")
            raise Exception()
        if toks[1] is None or not (toks[1].type == Token.TokenType.SEMICOLON or toks[1].type == Token.TokenType.LBRACE):
            print("Function declaration missing semicolon ';' or open brace '{'")
            raise Exception()
        
        func: Function = Function(None, None, None, None, name, None, params, None)
        if toks[1].type == Token.TokenType.LBRACE:
            body: FunctionBody = self.parse_function_body()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Function Body is not closed ...")
                raise Exception()
            func.body = body

        return func
        
    def parse_start_params(self) -> list[Parameter]:
        '''
        StartParams : Params | empty
        '''
        if self.debug_mode: print("Start Param check")

        tok: Token = self.lexer.peek_next()
        if tok is None: return None
        elif tok.type == Token.TokenType.RPAREN: return []
        elif tok.type == Token.TokenType.IDENTIFIER: return self.parse_params()
        else: return None

    def parse_params(self) -> list[Parameter]:
        '''
        Params : IDENTIFIER IDENTIFIER COMMA Params
                | IDENTIFIER IDENTIFIER
        '''
        if self.debug_mode: ("Param")
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            print("Expected parameter type ...")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Expected parameter name ...")
            raise Exception()
        param: Parameter = Parameter(toks[0].content, toks[1].content)

        tok: Token = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.COMMA: return [param]
        self.lexer.pop_token()

        params: list[Parameter] = self.parse_params()
        params.insert(0, param)
        return params

    def parse_function_body(self) -> FunctionBody:
        '''
        FunctionBody : COMMENT
                      | VariableDeclaration
        '''
        if self.debug_mode: print("Function Body check")
        tok: Token = self.lexer.peek_next()
        if tok is None: return None

        if tok.type == Token.TokenType.COMMENT:
            self.lexer.pop_token()
            return FunctionBody()

        return FunctionBody() # Empty function body
    
    def parse_start_args(self) -> list[Expression]:
        '''
        StartArgs : Args | empty
        '''
        if self.debug_mode: print("Start Args check")

        tok: Token = self.lexer.peek_next()
        if tok is None: return None
        elif tok.type == Token.TokenType.RPAREN: return []
        elif tok.type == Token.TokenType.IDENTIFIER: return self.parse_args()
        else: return None

    def parse_args(self) -> list[Expression]:
        '''
        Args : Expression COMMA Args 
              | Expression
        '''
        if self.debug_mode: print("Args check")
        exp: Expression = self.parse_expression()

        tok: Token = self.lexer.peek_next()
        if tok is None: return [exp]
        elif tok.type == Token.TokenType.COMMA:
            self.lexer.pop_token()
            return [exp, self.parse_args()]
        
        print("Unexpected end of arguments ...")
        raise Exception()

    def parse_expression(self) -> Expression:
        '''
        Expression : MemberAccess
                    | VAL
                    | Expression ADD Expression
                    | Expression SUB Expression
                    | Expression MULT Expression
                    | Expression DIV Expression
                    | Expression MOD Expression
        '''
        if self.debug_mode: print("Expression check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Reached unexpected end of file ...")
            raise Exception()
        elif tok.type == Token.TokenType.IDENTIFIER:
            left = Expression(self.parse_member_access())
        elif tok.type == Token.TokenType.VAL:
            self.lexer.pop_token()
            left = Expression(tok.content)
        else:
            print("Unexpected token in expression ...")
            raise Exception()
        
        tok: Token = self.lexer.next_token()
        if tok is None: return left

        if tok.type == Token.TokenType.ADD or tok.type == Token.TokenType.SUB or  tok.type == Token.TokenType.MULT or  tok.type == Token.TokenType.DIV or  tok.type == Token.TokenType.MOD:
            for op in Operation:
                if tok.content == op.value:
                    return Expression(None, left, self.parse_expression(), op)
                
        print("No valid operation found in expression ...")
        raise Exception()

    def parse_member_access(self) -> MemberAccess:
        '''
        MemberAccess : IDENTIFIER DOT MemberAccess
                      | FunctionCall
                      | IDENTIFIER
        '''
        if self.debug_mode: print("Member Access check")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            print("Member access has no name ...")
            raise Exception()
        if toks[1] is None or not (toks[1].type == Token.TokenType.DOT or toks[1] == Token.TokenType.LPAREN):
            self.lexer.pop_token()
            return MemberAccess(toks[0].content)
        
        if toks[1].type == Token.TokenType.DOT:
            self.lexer.pop_tokens(2)
            return MemberAccess(toks[0].content, None, self.parse_member_access())
        
        if toks[1].type == Token.TokenType.LPAREN:
            return MemberAccess(toks[0].content, self.parse_function_call(), self.parse_member_access())
        
        print("Member access parsing failed ...")
        return None

    def parse_function_call(self) -> FunctionCall:
        '''
        FunctionCall : IDENTIFIER LPAREN StartArgs RPAREN
        '''
        if self.debug_mode: print("Function Call check")
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            print("Function call has no name")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.LPAREN:
            print("Function call missing open parenthesis '('")
            raise Exception()
        
        args: list[Expression] = self.parse_start_args()
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Function call has missing close parenthesis ')'")
            raise Exception()
        
        return FunctionCall(toks[0].content, args)
        