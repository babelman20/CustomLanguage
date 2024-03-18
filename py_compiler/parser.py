from core_elements import *
from lexer import Lexer, Token

class Parser:

    def __init__(self, lexer: Lexer, debug_mode: bool = False):
        self.lexer: Lexer = lexer
        self.debug_mode: bool = debug_mode

    def parse(self) -> Program:
        '''
        Program : Mods ClassDeclaration
        '''
        if self.debug_mode: print("Program START")
        
        mods: list[str] = self.parse_mods()

        class_declaration: Class = self.parse_class_declaration()
        class_declaration.mods = mods

        return Program(class_declaration)

    def parse_mods(self) -> list[str]:
        '''
        Mods : PUBLIC Mods
              | STATIC Mods
              | SEALED Mods
              | ABSTRACT Mods
              | MUTABLE Mods
              | empty
        '''
        if self.debug_mode: print("Modifier check")

        mods: list[str] = []
        tok: Token = self.lexer.peek_next()
        while not tok is None and tok.type in self.lexer.MODS:
            mods.append(tok.content)
            self.lexer.pop_token()
            tok = self.lexer.peek_next()
        
        return mods

    def parse_class_declaration(self) -> Class:
        '''
        ClassDeclaration : CLASS IDENTIFIER ClassExtension LBRACE ClassBody RBRACE
        '''
        if self.debug_mode: print("Class declaration")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.CLASS:
            print("Class declaration missing 'class' keyword")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Class declaration missing a name")
            raise Exception()
        
        self.lexer.pop_tokens(2)
        extension: str = self.parse_class_extension()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            print("Class body is missing open brace '{'")
            raise Exception()
        
        body: ClassBody = self.parse_class_body()
        return Class(None, toks[1].content, extension, body)

    def parse_class_extension(self) -> str:
        '''
        ClassExtension : EXTENDS IDENTIFIER | empty
        '''
        if self.debug_mode: print("Class Extension check")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.EXTENDS: return None
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER: 
            print("Class extension missing name ...")
            raise Exception()
        
        self.lexer.pop_tokens(2)
        return toks[1].content

    def parse_class_body(self) -> ClassBody:
        '''
        ClassBody : Mods Constructor|ClassDeclaration|FunctionDeclaration|VariableDeclaration ClassBody 
                   | empty
        '''
        if self.debug_mode: ("Class Body")

        mods: list[str] = self.parse_mods()

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            print("Class body missing close brace '}'")
            raise Exception()
        elif toks[0].type == Token.TokenType.RBRACE:
            if self.debug_mode: print("End of class body")
            return ClassBody([],[],[],[])
        elif toks[0].type == Token.TokenType.CONSTRUCTOR:
            self.lexer.pop_token()
            member = self.parse_constructor()
        elif toks[0].type == Token.TokenType.CLASS:
            member = self.parse_class_declaration()
        elif toks[0].type == Token.TokenType.IDENTIFIER:
            if toks[1] is None:
                print("Unexpected end of file ...")
                raise Exception()
            elif toks[1].type == Token.TokenType.FUNCTION:
                member = self.parse_function_declaration()
            else:
                member = self.parse_variable_declaration()
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    print("Expected semicolon ';' to follow variable declaration")
                    raise Exception()
        else:
            print("Expected member in class body ...")
            raise Exception()
        
        member.mods = mods
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
        
        body: Body = self.parse_body()
        if self.debug_mode: print("Complete function body")
        
        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            print("Constructor missing close brace '}'")
            raise Exception()
        
        return Constructor(None, params, body)

    def parse_variable_declaration(self) -> Variable:
        '''
        VariableDeclaration : IDENTIFIER IDENTIFIER
                             | IDENTIFIER IDENTIFIER Initialization
        '''
        if self.debug_mode: print("Variable Declaration")
        
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file ...")
            raise Exception()
        
        if not toks[0].type == Token.TokenType.IDENTIFIER:
            print("Variable declaration missing type")
            raise Exception()
        if not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Variable declaration missing name")
            raise Exception()
        var_type: str = toks[0].content
        name: str = toks[1].content

        tok: Token = self.lexer.peek_next()
        if not tok is None and tok.type == Token.TokenType.SET:
            init_val: Expression = self.parse_initialization()
        else:
            init_val = None

        return Variable([], var_type, name, init_val)

    def parse_initialization(self) -> Expression:
        '''
        Initialization : SET Expression
        '''
        if self.debug_mode: print("Initialization")

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SET:
            print("Variable initialization missing '='")
            raise Exception()
        
        return self.parse_expression()

    def parse_function_declaration(self) -> Function:
        '''
        FunctionDeclaration : IDENTIFIER FUNCTION IDENTIFIER LPAREN StartParams RPAREN SEMICOLON
                             | IDENTIFIER FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
                             | IDENTIFIER FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        if self.debug_mode: print("Function Declaration")
        
        toks: list[Token] = self.lexer.next_tokens(4)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            print("Function return type not specified")
            raise Exception()
        return_type: str = toks[0].content
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
        
        func: Function = Function(None, name, return_type, params, None)
        if toks[1].type == Token.TokenType.LBRACE:
            body: Body = self.parse_body()
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
        Expression : ConstructorCall
                    | MemberAccess
                    | VAL
                    | LPAREN Expression RPAREN ADD|SUB|MULT|DIV|MOD Expression
                    | Expression ADD|SUB|MULT|DIV|MOD Expression
        '''
        if self.debug_mode: print("Expression check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Reached unexpected end of file ...")
            raise Exception()
        elif tok.type == Token.TokenType.LPAREN:
            self.lexer.pop_token()
            left = self.parse_expression()
        elif tok.type == Token.TokenType.NEW:
            left = Expression(self.parse_constructor_call())
        elif tok.type == Token.TokenType.IDENTIFIER:
            left = Expression(self.parse_member_access())
        elif tok.type == Token.TokenType.VAL:
            self.lexer.pop_token()
            left = Expression(tok.content)
        else:
            print("Unexpected token in expression ...")
            raise Exception()
        
        tok: Token = self.lexer.peek_next()
        if tok is None or tok.type not in [Token.TokenType.ADD, Token.TokenType.SUB, Token.TokenType.MULT, Token.TokenType.DIV, Token.TokenType.MOD]: return left
        self.lexer.pop_token()

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
    
    def parse_constructor_call(self) -> FunctionCall:
        '''
        ConstructorCall : NEW FunctionCall
        '''
        if self.debug_mode: print("Constructor Call check")
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.NEW:
            print("Constructor call has no 'new' keyword")
            raise Exception()
        self.lexer.pop_token()
        
        return self.parse_function_call()

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
    
    def parse_body(self) -> Body:
        '''
        Body : Statement Body
              | empty
        '''
        if self.debug_mode: print("Body check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Reached end of program unexpectedly ...")
            raise Exception()
        elif tok.type == Token.TokenType.RBRACE: return Body([]) # End of body

        statement: Statement = self.parse_statement()
        body = self.parse_body()
        body.statements.insert(0, statement)
        return body
    
    def parse_statement(self) -> Statement:
        '''
        Statement : IfBlock
                   | WhileBlock
                   | ForBlock
                   | ForEachBlock
                   | Switch
                   | FunctionCall (IDENTIFIER LPAREN or IDENTIFIER DOT)
                   | VariableDeclaration (IDENTIFIER IDENTIFIER)
                   | VariableUpdate SEMICOLON (IDENTIFIER (ADD|SUB|MULT|DIV|MOD|empty)SET or INC|DEC IDENTIFIER or IDENTIFIER INC|DEC)
                   | Return
                   | BREAK SEMICOLON
        '''
        if self.debug_mode: print("Statment check")

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            print("Reached unexpected end of file ...")
            raise Exception()

        if toks[0].type == Token.TokenType.IF:
            return Statement(self.parse_if_block())
        elif toks[0].type == Token.TokenType.WHILE:
            return Statement(self.parse_while_block())
        elif toks[0].type == Token.TokenType.FOR:
            return Statement(self.parse_for_block())
        elif toks[0].type == Token.TokenType.FOREACH:
           return Statement(self.parse_foreach_block())
        elif toks[0].type == Token.TokenType.SWITCH:
            return Statement(self.parse_switch())
        elif toks[0].type == Token.TokenType.BREAK:
            if toks[1] is None or not toks[1].type == Token.TokenType.SEMICOLON:
                print("Expected semicolon ';' after break statement")
                raise Exception()
            self.lexer.pop_tokens(2)
            return Statement(Break())
        elif toks[0].type == Token.TokenType.RETURN:
           return Statement(self.parse_return())
        elif toks[0].type == Token.TokenType.INC or toks[0].type == Token.TokenType.DEC:
            var_update = self.parse_variable_update()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                print("Variable update missing semicolon ';'")
                raise Exception()
            return Statement(var_update)
        elif toks[0].type == Token.TokenType.IDENTIFIER:
            if toks[1].type == Token.TokenType.LPAREN or toks[1].type == Token.TokenType.DOT:
                return Statement(self.parse_function_call())
            elif toks[1].type == Token.TokenType.IDENTIFIER:
                var_delcr = self.parse_variable_declaration()
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    print("Expected semicolon ';' to follow variable declaration")
                    raise Exception()
                return Statement(var_delcr)
            elif toks[1].type in [Token.TokenType.INC, Token.TokenType.DEC, Token.TokenType.SET,
                                  Token.TokenType.ADD, Token.TokenType.SUB, Token.TokenType.MULT, Token.TokenType.DIV, Token.TokenType.MOD]:
                var_update = self.parse_variable_update()
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    print("Variable update missing semicolon ';'")
                    raise Exception()
                return Statement(var_update)

        print(f"Unrecognized statement starting with: {toks[0].content} {toks[1].content}")
        raise Exception()
    
    def parse_return(self) -> Return:
        '''
        Return : RETURN SEMICOLON
                | RETURN Expression SEMICOLON
        '''
        if self.debug_mode: print("Return check")

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RETURN:
            print("Expected 'return' keyword")
            raise Exception()
        
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Unexpected end of file")
            raise Exception()
        elif not tok.type == Token.TokenType.SEMICOLON: val = self.parse_expression()
        else: val = None

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            print("Expected semicolon ';' after return statement")
            raise Exception()
        return Return(val)

    def parse_if_block(self) -> If:
        '''
        IfBlock : IF LPAREN Conditions RPAREN LBRACE Block RBRACE
                 | IF LPAREN Conditions RPAREN LBRACE Block RBRACE ELSE IfBlock
                 | IF LPAREN Conditions RPAREN LBRACE Block RBRACE ElSE LBRACE Block RBRACE
                 | IF LPAREN Conditions RPAREN LBRACE Block RBRACE ELSE Statement

                 | IF LPAREN Conditions RPAREN Statement
                 | IF LPAREN Conditions RPAREN Statement ELSE IfBlock
                 | IF LPAREN Conditions RPAREN Statement Else LBRACE Block RBRACE
                 | IF LPAREN Conditions RPAREN Statement ELSE Statement                
        '''
        if self.debug_mode: print("If block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.IF or not toks[1].type == Token.TokenType.LPAREN:
            print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Invalid end of IF statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Invalid end of IF statement body")
                raise Exception()

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.ELSE: return If(conditions, content, [], None)
        self.lexer.pop_token()

        if toks[1] is None:
            print("Unexpected end of file ...")
            raise Exception()
        elif toks[1].type == Token.TokenType.LBRACE: # Else condition
            self.lexer.pop_token()
            els = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Invalid end of IF statement body")
                raise Exception()
            return If(conditions, content, [], els)
        elif toks[1].type == Token.TokenType.IF: # Else If block
            next_if = self.parse_if_block()
            elifs = next_if.elseifs
            els = next_if.els
            next_if.elseifs = []
            next_if.els = None
            elifs.insert(0, next_if)
            return If(conditions, content, elifs, els) 
        else: # Else statement
            els = self.parse_statement()
            return If(conditions, content, [], els) 

    def parse_while_block(self) -> While:
        '''
        WhileBlock : WHILE LPAREN Conditions RPAREN LBRACE Block RBRACE
                    | WHILE LPAREN Conditions RPAREN Statement               
        '''
        if self.debug_mode: print("While block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.WHILE or not toks[1].type == Token.TokenType.LPAREN:
            print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Invalid end of WHILE statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Invalid end of WHILE statement body")
                raise Exception()
        
        return While(conditions, content)

    def parse_for_block(self) -> For:
        '''
        ForBlock : FOR LPAREN VariableDeclaration SEMICOLON Conditions SEMICOLON VariableUpdate RPAREN LBRACE Block RBRACE
                  | FOR LPAREN VariableDeclaration SEMICOLON Conditions SEMICOLON VariableUpdate RPAREN Statement               
        '''
        if self.debug_mode: print("For block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.FOR or not toks[1].type == Token.TokenType.LPAREN:
            print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        var_declr: Variable = self.parse_variable_declaration()
        
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            print("Expected semicolon ';' to follow variable declaration")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            print("Expected semicolon ';' following conditions")
            raise Exception()
        
        var_update: VariableUpdate = self.parse_variable_update()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            print("Invalid end of FOR statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Invalid end of FOR statement body")
                raise Exception()
        
        return For(var_declr, conditions, var_update, content)

    def parse_foreach_block(self) -> ForEach:
        '''
        ForBlock : FOREACH LPAREN VariableDeclaration IN IDENTIFIER RPAREN LBRACE Block RBRACE
                  | FOREACH LPAREN VariableDeclaration IN IDENTIFIER RPAREN Statement         
        '''
        if self.debug_mode: print("ForEach block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.FOREACH or not toks[1].type == Token.TokenType.LPAREN:
            print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        var_declr: Variable = self.parse_variable_declaration()

        toks: list[Token] = self.lexer.next_tokens(3)
        if toks[0] is None or not toks[0].type == Token.TokenType.IN:
            print("Expected 'in' keyword in ForEach statement")
            raise Exception()
        elif toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            print("Expected iterable variable in ForEach statement")
            raise Exception()
        elif toks[2] is None or not toks[2].type == Token.TokenType.RPAREN:
            print("ForEach statement missing close parenthesis ')'")
            raise Exception()
        iterable_var: str = toks[1].content

        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                print("Invalid end of FOR statement body")
                raise Exception()
            
        return ForEach(var_declr, iterable_var, content)
    
    def parse_switch(self) -> Switch:
        '''
        Switch : SWITCH LPAREN Expression RPAREN LBRACE Cases RBRACE
        '''
        if self.debug_mode: print("Switch block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.SWITCH or not toks[1].type == Token.TokenType.LPAREN:
            print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        test_val: Expression = self.parse_expression()

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.RPAREN:
            print("Switch statement missing close parenthesis ')'")
            raise Exception()
        elif not toks[1].type == Token.TokenType.LBRACE:
            print("Switch statement missing open brace '{'")
            raise Exception()
        
        cases: list[Case] = self.parse_cases()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            print("Switch statement missing close brace '}'")
            raise Exception()
        
        return Switch(test_val, cases)

    def parse_cases(self) -> list[Case]:
        '''
        Cases : Case Cases
               | Case
               | DEFAULT COLON Casebody
        '''
        if self.debug_mode: print("Getting switch cases")

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            print("Unexpected end of file ...")
            raise Exception()
        elif toks[0].type == Token.TokenType.DEFAULT:
            if not toks[1].type == Token.TokenType.COLON:
                print("Default case missing colon ':'")
                raise Exception()
            self.lexer.pop_tokens(2)
            return [Case(None, self.parse_case_body(True))]
        elif toks[0].type == Token.TokenType.CASE:
            c: Case = self.parse_case()
            tok: Token = self.lexer.peek_next()
            if tok is None:
                print("Unexpected end of file ...")
                raise Exception()
            elif tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT:
                cases: list[Case] = self.parse_cases()
                cases.insert(0, c)
                return cases
            else: return [c]
        else:
            print("Expected 'case' or 'default' in switch block")
            raise Exception()

    
    def parse_case(self) -> Case:
        '''
        Case : CASE Expression COLON CaseBody
        '''
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.CASE:
            print("Case missing 'case' keyword")
            raise Exception()
        
        val: Expression = self.parse_expression()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.COLON:
            print("Case missing colon ':'")
            raise Exception()
        
        body: Body = self.parse_case_body(False)
        return Case(val, body)

    def parse_case_body(self, isDefault: bool) -> CaseBody:
        '''
        CaseBody : BREAK SEMICOLON
                  | Return
                  | Statement CaseBody
                  | empty
        '''
        if self.debug_mode: print("Case Body check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Reached end of program unexpectedly ...")
            raise Exception()
        elif isDefault:
            if tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT:
                print("'default' must be final case in switch block!")
                raise Exception()
            elif tok.type == Token.TokenType.RBRACE: return CaseBody([])
        elif tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT: return None # Next case is coming up

        if tok.type == Token.TokenType.BREAK:
            self.lexer.pop_token()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                print("Expected semicolon ';' after break statement")
                raise Exception()
            return CaseBody([Statement(Break())])
        elif tok.type == Token.TokenType.RETURN:
            ret: Return = self.parse_return()
            return CaseBody([Statement(ret)])

        statement: Statement = self.parse_statement()
        body: CaseBody = self.parse_case_body(isDefault)
        if body is None: return Body([statement])
        else:
            body.statements.insert(0, statement)
            return body

    def parse_conditions(self) -> Conditions:
        '''
        Conditions : LPAREN Conditions RPAREN AND|OR Conditions
                    | NOT LPAREN Conditions RPAREN AND|OR Conditions
                    | Condition AND|OR Conditions
                    | NOT Conditions
                    | Condition
        '''
        if self.debug_mode: print("Conditions check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            print("Reached unexpected end of file ...")
            raise Exception()
        elif tok.type == Token.TokenType.NOT:
            self.lexer.pop_token()
            tok: Token = self.lexer.peek_next()
            if tok is None:
                print("Reached unexpected end of file ...")
                raise Exception()
            inversed = True
        else:
            inversed = False

        if tok.type == Token.TokenType.LPAREN:
            self.lexer.pop_token()
            left = self.parse_conditions()
            self.lexer.pop_token()
        else:
            left = self.parse_condition()
        left.inversed = inversed
        
        tok: Token = self.lexer.peek_next()
        if tok is None or not (tok.type == Token.TokenType.AND or tok.type == Token.TokenType.OR): return left
        self.lexer.pop_token()

        if tok.type == Token.TokenType.AND:
            return Conditions(None, True, None, left, self.parse_conditions())
        elif tok.type == Token.TokenType.OR:
             return Conditions(None, False, None, left, self.parse_conditions())
                
        print("No valid operation found in condition ...")
        raise Exception()

    def parse_condition(self) -> Conditions:
        '''
        Condition : Expression LT Expression
                    | Expression LEQ Expression
                    | Expression GT Expression
                    | Expression GEQ Expression
                    | Expression NEQ Expression
                    | Expression EQ Expression
        '''
        if self.debug_mode: print("Condition")

        left = self.parse_expression()

        tok: Token = self.lexer.next_token()
        
        cond_op = None
        for op in ConditionOperation:
            if tok.content == op.value:
                cond_op = op
                break

        if cond_op is None:
            print(f"Invalid condition operation: {tok.content}")
            raise Exception()
        
        right = self.parse_expression()

        return Conditions(None, None, Condition(left, right, op))
    
    def parse_variable_update(self):
        '''
        VariableUpdate : IDENTIFIER (ADD|SUB|MULT|DIV|MOD|empty) SET Expression
                        | INC IDENTIFIER
                        | DEC IDENTIFIER
                        | IDENTIFIER INC
                        | IDENTIFIER DEC
        '''
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            print("Unexpected end of file ...")
            raise Exception()
        
        if toks[0].type == Token.TokenType.INC or toks[0].type == Token.TokenType.DEC:
            if toks[1].type == Token.TokenType.IDENTIFIER:
                if toks[0].type == Token.TokenType.INC: return VariableUpdate(toks[1].content, VariableSetOperation.INC, True)
                else: return VariableUpdate(toks[1].content, VariableSetOperation.DEC, True)
            else:
                print(f"Expected variable name after {toks[0].content}")
                raise Exception()
        elif toks[0].type == Token.TokenType.IDENTIFIER:
            if toks[1].type == Token.TokenType.INC: return VariableUpdate(toks[0].content, VariableSetOperation.INC, False)
            elif toks[1].type == Token.TokenType.DEC: return VariableUpdate(toks[0].content, VariableSetOperation.DEC, False)
            elif toks[1].type == Token.TokenType.SET:
                return VariableUpdate(toks[0].content, VariableSetOperation.SET, self.parse_expression())
            else:
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SET:
                    print(f"Expected '=' after variable")
                    raise Exception()
                
                content = toks[1].content + '='
                update_op = None
                for op in VariableSetOperation:
                    if content == op.value:
                        update_op = op
                        break
                if update_op is None:
                    print(f"Unrecognized operation: {toks[1].content}")
                    raise Exception()
                return VariableUpdate(toks[0].content, update_op, self.parse_expression())
        else:
            print(f"Unexpected token: {toks[0].content}")
            raise Exception()
        