from .core_elements import *
from .lexer import Lexer, Token

class Parser:

    def __init__(self, lexer: Lexer, debug_mode: bool = False, suppress_err: bool = False):
        self.lexer: Lexer = lexer
        self.debug_mode: bool = debug_mode
        self.suppress_err: bool = suppress_err

    def parse_class(self) -> Class:
        '''
        Program : Mods ClassDeclaration
        '''
        if self.debug_mode: print("Program START")
        
        mods: list[str] = self.parse_mods()

        class_declaration: Class = self.parse_class_declaration()
        class_declaration.mods = mods

        return class_declaration

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
        ClassDeclaration : CLASS IDENTIFIER Class Typedef Extension LBRACE ClassBody RBRACE
        '''
        if self.debug_mode: print("Class declaration")
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.CLASS:
            if not self.suppress_err: print("Class declaration missing 'class' keyword")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Class declaration missing a name")
            raise Exception()
        
        typedefs: list[str] = self.parse_typedef()
        extension: str = self.parse_class_extension()
        
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            if not self.suppress_err: print("Class body is missing open brace '{'")
            raise Exception()
        
        body: ClassBody = self.parse_class_body()
        return Class(None, toks[1].content, typedefs, extension, body)
    
    def parse_typedef(self) -> list[str]:
        '''
        Typedef : LT IDENTIFIER (COMMA IDENTIFIER)* GT
        '''
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or toks[0].type is not Token.TokenType.LT: return None
        if toks[1] is None or toks[1].type is not Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Typedef not given a name ... ")
            raise Exception()
        typedefs: list[str] = [toks[1].content]
        
        self.lexer.pop_tokens(2)

        toks: list[Token] = self.lexer.peek_tokens(2)
        while toks[0] is not None and toks[0].type is Token.TokenType.COMMA:
            if toks[1] is None or toks[1].type is not Token.TokenType.IDENTIFIER:
                if not self.suppress_err: print("Typedef not given a name ... ")
                raise Exception()
            typedefs.append(toks[1].content)
            self.lexer.pop_tokens(2)
            toks = self.lexer.peek_tokens(2)
        
        tok: Token = self.lexer.next_token()
        if tok is None or tok.type is not Token.TokenType.GT:
            if not self.suppress_err: print("Typedef missing close '>'")
            raise Exception()
        
        return typedefs
        
    def parse_class_extension(self) -> str:
        '''
        ClassExtension : EXTENDS IDENTIFIER | empty
        '''
        if self.debug_mode: print("Class Extension check")
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.EXTENDS: return None
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER: 
            if not self.suppress_err: print("Class extension missing name ...")
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
            if not self.suppress_err: print("Class body missing close brace '}'")
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
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            elif toks[1].type == Token.TokenType.FUNCTION:
                member = self.parse_function_declaration()
            else:
                member = self.parse_variable_declaration()
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    if not self.suppress_err: print("Expected semicolon ';' to follow variable declaration")
                    raise Exception()
        else:
            if not self.suppress_err: print("Expected member in class body ...")
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
            if not self.suppress_err: print(f"Received unhandled class body member type: {type(member)}")
            raise Exception()
        return body

    def parse_constructor(self) -> Constructor:
        '''
        Constructor : LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        if self.debug_mode: print("Class Body")
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LPAREN:
            if not self.suppress_err: print("Constructor missing open parenthesis '('")
            raise Exception()

        params: list[Parameter] = self.parse_start_params()
        if params is None:
            if not self.suppress_err: print("Constructor parameters missing ...")
            raise Exception()

        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Constructor missing close parenthesis ')'")
            raise Exception()
        
        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LBRACE:
            if not self.suppress_err: print("Constructor missing open brace '{'")
            raise Exception()
        
        body: Body = self.parse_body()
        if self.debug_mode: print("Complete function body")
        
        tok = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            if not self.suppress_err: print("Constructor missing close brace '}'")
            raise Exception()
        
        return Constructor(None, params, body)

    def parse_variable_declaration(self) -> Variable:
        '''
        VariableDeclaration : IDENTIFIER IDENTIFIER
                             | IDENTIFIER IDENTIFIER Initialization
                             | IDENTIFIER Typedef IDENTIFIER
                             | IDENTIFIER Typedef IDENTIFIER Initialization
        '''
        if self.debug_mode: print("Variable Declaration")
        
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Variable declaration missing type")
            raise Exception()
        var_type: str = tok.content
        
        tok: Token = self.lexer.peek_next()
        if not tok is None and tok.type == Token.TokenType.LT:
            typedef: list[str] = self.parse_typedef()
        else:
            typedef = []

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Variable declaration missing name")
            raise Exception()
        name: str = tok.content
        pos: int = tok.pos

        tok: Token = self.lexer.peek_next()
        if not tok is None and tok.type == Token.TokenType.SET:
            val: Expression = self.parse_initialization()
        else:
            val = None

        return Variable([], var_type, typedef, name, pos, val)

    def parse_initialization(self) -> Expression:
        '''
        Initialization : SET Expression
        '''
        if self.debug_mode: print("Initialization")

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SET:
            if not self.suppress_err: print("Variable initialization missing '='")
            raise Exception()
        
        return self.parse_expression()

    def parse_function_declaration(self) -> Function:
        '''
        FunctionDeclaration : IDENTIFIER FUNCTION IDENTIFIER LPAREN StartParams RPAREN SEMICOLON
                             | IDENTIFIER FUNCTION IDENTIFIER LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
                             | IDENTIFIER FUNCTION OPERATOR Operation LPAREN StartParams RPAREN LBRACE FunctionBody RBRACE
        '''
        if self.debug_mode: print("Function Declaration")
        
        toks: list[Token] = self.lexer.next_tokens(3)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Function return type not specified")
            raise Exception()
        return_type: str = toks[0].content
        if toks[1] is None or not toks[1].type == Token.TokenType.FUNCTION:
            if not self.suppress_err: print("Function declaration not specified")
            raise Exception()
        if toks[2] is None:
            if not self.suppress_err: print("Function declaration missing name")
            raise Exception()
        elif toks[2].type == Token.TokenType.OPERATOR:
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.content in [op.value for op in all_operations]:
                if not self.suppress_err: print(f"Operator overloading requires real operation, not {tok.content}")
                raise Exception()
            name: str = 'operator_' + str(tok.type).removeprefix('TokenType.')
        elif not toks[2].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Function declaration missing name")
            raise Exception()
        else: name: str = toks[2].content

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LPAREN:
            if not self.suppress_err: print("Function declaration missing open parenthesis '('")
            raise Exception()
                
        params: list[Parameter] = self.parse_start_params()
        if params is None:
            if not self.suppress_err: print("Function parameters missing ...")
            raise Exception()

        toks = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Function parameters missing close parenthesis ')'")
            raise Exception()
        if toks[1] is None or not (toks[1].type == Token.TokenType.SEMICOLON or toks[1].type == Token.TokenType.LBRACE):
            if not self.suppress_err: print("Function declaration missing semicolon ';' or open brace '{'")
            raise Exception()
        
        func: Function = Function(None, name, return_type, params, None)
        if toks[1].type == Token.TokenType.LBRACE:
            body: Body = self.parse_body()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Function Body is not closed ...")
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
        Params : IDENTIFIER Typedef IDENTIFIER COMMA Params
                | IDENTIFIER Typedef IDENTIFIER
        '''
        if self.debug_mode: ("Param")
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Expected parameter type ...")
            raise Exception()
        type = tok.content
        
        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif tok.type == Token.TokenType.LT:
            typedef: list[str] = self.parse_typedef()
        else:
            typedef = None

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Expected parameter name ...")
            raise Exception()
        name = tok.content

        param: Parameter = Parameter(type, typedef, name)

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
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif tok.type == Token.TokenType.RPAREN: return []
        else: return self.parse_args()

    def parse_args(self) -> list[Expression]:
        '''
        Args : Expression COMMA Args 
              | Expression
        '''
        if self.debug_mode: print("Args check")
        exp: Expression = self.parse_expression()
        exps = [exp]

        tok: Token = self.lexer.peek_next()
        while tok.type == Token.TokenType.COMMA:
            self.lexer.pop_token()
            exps.append(self.parse_expression())
            tok: Token = self.lexer.peek_next()
        return exps

    def parse_expression(self) -> Expression:
        '''
        Expression : IDENTIFIER
                    | FunctionCall
                    | ConstructorCall
                    | MemberAccess
                    | VAL
                    | LPAREN Expression RPAREN Operator Expression
                    | Expression Operator Expression
        '''
        if self.debug_mode: print("Expression check")
        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Reached unexpected end of file ...")
            raise Exception()
        
        values: list[Expression] = []
        operations: list[Operation] = []
        while tok is not None:     
            if tok.type == Token.TokenType.LPAREN:
                self.lexer.pop_token()
                values.append(self.parse_expression())
                tok: Token = self.lexer.peek_next()
                if tok is None or tok.type is not Token.TokenType.RPAREN:
                    if not self.suppress_err: print("Expected close parenthesis ')'")
                    raise Exception()
                self.lexer.pop_token()
            elif tok.type == Token.TokenType.VAL:
                self.lexer.pop_token()
                values.append(Value(tok.content))
            else:
                values.append(self.parse_member_access())
        
            tok: Token = self.lexer.peek_next()
            if tok is None:
                if not self.suppress_err: print("Reached unexpected end of file ...")
                raise Exception()
            elif not tok.content in [op.value for op in expression_operations]: break
            
            for op in expression_operations:
                if tok.content == op.value:
                    operations.append(op)
                    break
            self.lexer.pop_token()

            if not len(values) == len(operations):
                if not self.suppress_err: print("No valid operation found in expression ...")
                raise Exception()

            tok: Token = self.lexer.peek_next()
        
        return Expression(values, operations)

    def parse_member_access(self) -> MemberAccess:
        '''
        MemberAccess : IDENTIFIER (DOT (IDENTIFIER | FunctionCall | ConstructorCall))*
                      | FunctionCall (DOT (IDENTIFIER | FunctionCall | ConstructorCall))*
                      | ConstructorCall (DOT (IDENTIFIER | FunctionCall | ConstructorCall))*
        '''
        if self.debug_mode: print("Member Access check")

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            if not self.suppress_err: print("Unexpected end of file ...")
            raise Exception()
        
        if toks[0].type == Token.TokenType.NEW:  # Constructor call
            content = self.parse_constructor_call()
        elif toks[0].type == Token.TokenType.IDENTIFIER:
            if toks[1] is None:
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            
            if toks[1].type == Token.TokenType.LPAREN:
                content = self.parse_function_call()
            else:
                content = VariableAccess(toks[0].content, toks[0].pos)
                self.lexer.pop_token()

        accesses = [content]
        tok = self.lexer.peek_next()
        while tok is not None and tok.type == Token.TokenType.DOT:
            self.lexer.pop_token()
            toks: list[Token] = self.lexer.peek_tokens(2)
            if toks[0] is None:
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            
            if toks[0].type == Token.TokenType.NEW:  # Constructor call
                content = self.parse_constructor_call()
            elif toks[0].type == Token.TokenType.IDENTIFIER:
                if toks[1] is None:
                    if not self.suppress_err: print("Unexpected end of file ...")
                    raise Exception()
                
                if toks[1].type == Token.TokenType.LPAREN:
                    content = self.parse_function_call()
                else:
                    content = VariableAccess(toks[0].content, toks[0].pos)
                    self.lexer.pop_token()
            accesses.append(content)
            tok = self.lexer.peek_next()

        return MemberAccess(accesses)
    
    def parse_constructor_call(self) -> ConstructorCall:
        '''
        ConstructorCall : NEW IDENTIFIER LPAREN StartArgs RPAREN
                        | NEW IDENTIFIER Typedef LPAREN StartArgs RPAREN
        '''
        if self.debug_mode: print("Constructor Call check")
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.NEW:
            if not self.suppress_err: print("Constructor call has no 'new' keyword")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Constructor call has no name")
            raise Exception()
        name = toks[1].content
        
        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif tok.type == Token.TokenType.LT:
            typedef: list[str] = self.parse_typedef()
        else:
            typedef = None

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.LPAREN:
            if not self.suppress_err: print("Constructor call missing open parenthesis '('")
            raise Exception()
        
        args: list[Expression] = self.parse_start_args()
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Constructor call has missing close parenthesis ')'")
            raise Exception()
        
        return ConstructorCall(name, typedef, args)

    def parse_function_call(self) -> FunctionCall:
        '''
        FunctionCall : IDENTIFIER LPAREN StartArgs RPAREN
        '''
        if self.debug_mode: print("Function Call check")
        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or not toks[0].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Function call has no name")
            raise Exception()
        if toks[1] is None or not toks[1].type == Token.TokenType.LPAREN:
            if not self.suppress_err: print("Function call missing open parenthesis '('")
            raise Exception()
        
        args: list[Expression] = self.parse_start_args()
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Function call has missing close parenthesis ')'")
            raise Exception()
        
        return FunctionCall(toks[0].content, args)
    
    def parse_body(self) -> Body:
        '''
        Body : Statement Body
              | empty
        '''
        if self.debug_mode: print("Body check")

        body = Body([])
        tok: Token = self.lexer.peek_next()
        while tok is not None and not tok.type == Token.TokenType.RBRACE:
            statement: Statement = self.parse_statement()
            body.statements.append(statement)
            tok: Token = self.lexer.peek_next()

        if tok is None:
            if not self.suppress_err: print("Reached end of program unexpectedly ...")
            raise Exception()
        
        return body
    
    def parse_statement(self) -> Statement:
        '''
        Statement : IfBlock
                   | WhileBlock
                   | ForBlock
                   | ForEachBlock
                   | Switch
                   | FunctionCall (IDENTIFIER LPAREN or IDENTIFIER DOT)
                   | VariableDeclaration (IDENTIFIER IDENTIFIER or IDENTIFIER Typedef IDENTIFIER)
                   | VariableUpdate SEMICOLON (IDENTIFIER (ADD|SUB|MULT|DIV|MOD|empty)SET or INC|DEC IDENTIFIER or IDENTIFIER INC|DEC)
                   | Return
                   | BREAK SEMICOLON
                   | AsmBlock
        '''
        if self.debug_mode: print("Statement check")

        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            if not self.suppress_err: print("Reached unexpected end of file ...")
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
                if not self.suppress_err: print("Expected semicolon ';' after break statement")
                raise Exception()
            self.lexer.pop_tokens(2)
            return Statement(Break())
        elif toks[0].type == Token.TokenType.RETURN:
           return Statement(self.parse_return())
        elif toks[0].type == Token.TokenType.ASM:
            return Statement(self.parse_asm_block())
        elif toks[0].type == Token.TokenType.INC or toks[0].type == Token.TokenType.DEC:
            var_update = self.parse_variable_update()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                if not self.suppress_err: print("Variable update missing semicolon ';'")
                raise Exception()
            return Statement(var_update)
        else:
            mods: list[str] = self.parse_mods()  # Get mods for potential variable declaration
            toks: list[Token] = self.lexer.peek_tokens(2)
            if toks[0].type == Token.TokenType.IDENTIFIER and (toks[1].type == Token.TokenType.IDENTIFIER or toks[1].type == Token.TokenType.LT):
                var_delcr = self.parse_variable_declaration()
                var_delcr.mods = mods

                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    if not self.suppress_err: print("Expected semicolon ';' to follow variable declaration")
                    raise Exception()
                return Statement(var_delcr)
            else:
                member_access = self.parse_member_access()
                if len(member_access.accesses) == 0:  member_access = None

                tok: Token = self.lexer.peek_next()
                if tok.type == Token.TokenType.SEMICOLON:  return Statement(member_access)

                # Only remaining option is variable update
                var_update = self.parse_variable_update(member_access)
                tok: Token = self.lexer.next_token()
                if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                    if not self.suppress_err: print("Variable update missing semicolon ';'")
                    raise Exception()
                return Statement(var_update)

    def parse_return(self) -> Return:
        '''
        Return : RETURN SEMICOLON
                | RETURN Expression SEMICOLON
        '''
        if self.debug_mode: print("Return check")

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RETURN:
            if not self.suppress_err: print("Expected 'return' keyword")
            raise Exception()
        
        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not tok.type == Token.TokenType.SEMICOLON: val = self.parse_expression()
        else: val = None

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            if not self.suppress_err: print("Expected semicolon ';' after return statement")
            raise Exception()
        return Return(val)
    
    def parse_asm_block(self) -> Asm:
        '''
        AsmBlock: ASM LBRACE QUOTE RBRACE 
        '''
        toks: list[Token] = self.lexer.next_tokens(4)
        if toks[0] is None or not toks[0].type == Token.TokenType.ASM:
            if not self.suppress_err: print("How did we access asm block with no asm ...")
            raise Exception()
        
        if toks[1] is None or not toks[1].type == Token.TokenType.LBRACE:
            if not self.suppress_err: print("Asm block missing open brace '{'")
            raise Exception()
        
        if toks[2] is None or not toks[2].type == Token.TokenType.QUOTE:
            if not self.suppress_err: print("Asm block missing content")
            raise Exception()
        
        if toks[3] is None or not toks[3].type == Token.TokenType.RBRACE:
            if not self.suppress_err: print("Asm block missing close brace '}'")
            raise Exception()
        
        return Asm(toks[2].content)


    def parse_if_block(self) -> If:
        '''
        IfBlock : IF (CONSTEXPR) LPAREN Conditions RPAREN LBRACE Block RBRACE (ELSE IfBlock) (ELSE LBRACE Block RBRACE)
                 | IF (CONSTEXPR) LPAREN Conditions RPAREN LBRACE Block RBRACE (ELSE IfBlock) (ELSE Statement)
                 | IF (CONSTEXPR) LPAREN Conditions RPAREN Statement (ELSE IfBlock) (ELSE LBRACE Block RBRACE)
                 | IF (CONSTEXPR) LPAREN Conditions RPAREN Statement (ELSE IfBlock) (ELSE Statement)            
        '''
        if self.debug_mode: print("If block check")

        tok: Token = self.lexer.next_token()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not tok.type == Token.TokenType.IF:
            if not self.suppress_err: print(f"Not an IF statement! {tok.content}")
            raise Exception()
        
        constexpr = False

        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif tok.type == Token.TokenType.CONSTEXPR:
            constexpr = True
            self.lexer.pop_token()
    
        tok: Token = self.lexer.next_token()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not tok.type == Token.TokenType.LPAREN:
            if not self.suppress_err: print(f"IF statement has no condition!")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Invalid end of IF statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Invalid end of IF statement body")
                raise Exception()
        
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is None:
            if not self.suppress_err: print("Unexpected end of file ...")
            raise Exception()
        elif not toks[0].type == Token.TokenType.ELSE: return If(constexpr, conditions, content, [], toks[0].pos)
        self.lexer.pop_token()

        if toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file ...")
            raise Exception()
        elif toks[1].type == Token.TokenType.LBRACE: # Else condition
            self.lexer.pop_token()
            els = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Invalid end of IF statement body")
                raise Exception()
            return If(constexpr, conditions, content, [], els, toks[1].pos)
        elif toks[1].type == Token.TokenType.IF: # Else If block
            next_if = self.parse_if_block()
            elifs = next_if.elseifs
            els = next_if.els
            next_if.elseifs = []
            next_if.els = None
            elifs.insert(0, next_if)
            return If(constexpr, conditions, content, elifs, els, toks[1].pos) 
        else: # Else statement
            els = self.parse_statement()
            return If(constexpr, conditions, content, [], els, toks[1].pos) 

    def parse_while_block(self) -> While:
        '''
        WhileBlock : WHILE LPAREN Conditions RPAREN LBRACE Block RBRACE
                    | WHILE LPAREN Conditions RPAREN Statement               
        '''
        if self.debug_mode: print("While block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.WHILE or not toks[1].type == Token.TokenType.LPAREN:
            if not self.suppress_err: print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Invalid end of WHILE statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: content = self.parse_statement()
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Invalid end of WHILE statement body")
                raise Exception()
            end_pos = tok.pos
        
        return While(conditions, content, end_pos)

    def parse_for_block(self) -> For:
        '''
        ForBlock : FOR LPAREN VariableDeclaration SEMICOLON Conditions SEMICOLON VariableUpdate RPAREN LBRACE Block RBRACE
                  | FOR LPAREN VariableDeclaration SEMICOLON Conditions SEMICOLON VariableUpdate RPAREN Statement               
        '''
        if self.debug_mode: print("For block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.FOR or not toks[1].type == Token.TokenType.LPAREN:
            if not self.suppress_err: print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        var_declr: Variable = self.parse_variable_declaration()
        
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            if not self.suppress_err: print("Expected semicolon ';' to follow variable declaration")
            raise Exception()
        
        conditions: Conditions = self.parse_conditions()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.SEMICOLON:
            if not self.suppress_err: print("Expected semicolon ';' following conditions")
            raise Exception()
        
        var_update: VariableUpdate = self.parse_variable_update()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Invalid end of FOR statement condition")
            raise Exception()
        
        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: 
            content = self.parse_statement()
            tok = self.lexer.peek_next()
            if tok is None:
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            end_pos = tok.pos
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Invalid end of FOR statement body")
                raise Exception()
            end_pos = tok.pos
        
        return For(var_declr, conditions, var_update, content, end_pos)

    def parse_foreach_block(self) -> ForEach:
        '''
        ForBlock : FOREACH LPAREN VariableDeclaration IN IDENTIFIER RPAREN LBRACE Block RBRACE
                  | FOREACH LPAREN VariableDeclaration IN IDENTIFIER RPAREN Statement         
        '''
        if self.debug_mode: print("ForEach block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.FOREACH or not toks[1].type == Token.TokenType.LPAREN:
            if not self.suppress_err: print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        var_declr: Variable = self.parse_variable_declaration()

        toks: list[Token] = self.lexer.next_tokens(3)
        if toks[0] is None or not toks[0].type == Token.TokenType.IN:
            if not self.suppress_err: print("Expected 'in' keyword in ForEach statement")
            raise Exception()
        elif toks[1] is None or not toks[1].type == Token.TokenType.IDENTIFIER:
            if not self.suppress_err: print("Expected iterable variable in ForEach statement")
            raise Exception()
        elif toks[2] is None or not toks[2].type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("ForEach statement missing close parenthesis ')'")
            raise Exception()
        iterable_var: VariableAccess = VariableAccess(toks[1].content, toks[1].pos)

        tok = self.lexer.peek_next()
        if tok is None or not tok.type == Token.TokenType.LBRACE: 
            content = self.parse_statement()
            tok = self.lexer.peek_next()
            if tok is None:
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            end_pos = tok.pos
        else:
            self.lexer.pop_token()
            content = self.parse_body()
            tok = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RBRACE:
                if not self.suppress_err: print("Invalid end of FOR statement body")
                raise Exception()
            end_pos = tok.pos
            
        return ForEach(var_declr, iterable_var, content, end_pos)
    
    def parse_switch(self) -> Switch:
        '''
        Switch : SWITCH LPAREN Expression RPAREN LBRACE Cases RBRACE
        '''
        if self.debug_mode: print("Switch block check")

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.SWITCH or not toks[1].type == Token.TokenType.LPAREN:
            if not self.suppress_err: print(f"Invalid statement: {toks[0].content} {toks[1].content}")
            raise Exception()
        
        test_val: Expression = self.parse_expression()

        toks: list[Token] = self.lexer.next_tokens(2)
        if toks[0] is None or toks[1] is None:
            if not self.suppress_err: print("Unexpected end of file")
            raise Exception()
        elif not toks[0].type == Token.TokenType.RPAREN:
            if not self.suppress_err: print("Switch statement missing close parenthesis ')'")
            raise Exception()
        elif not toks[1].type == Token.TokenType.LBRACE:
            if not self.suppress_err: print("Switch statement missing open brace '{'")
            raise Exception()
        
        cases: list[Case] = self.parse_cases()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.RBRACE:
            if not self.suppress_err: print("Switch statement missing close brace '}'")
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
            if not self.suppress_err: print("Unexpected end of file ...")
            raise Exception()
        elif toks[0].type == Token.TokenType.DEFAULT:
            if not toks[1].type == Token.TokenType.COLON:
                if not self.suppress_err: print("Default case missing colon ':'")
                raise Exception()
            self.lexer.pop_tokens(2)
            return [Case(None, self.parse_case_body(True))]
        elif toks[0].type == Token.TokenType.CASE:
            c: Case = self.parse_case()
            tok: Token = self.lexer.peek_next()
            if tok is None:
                if not self.suppress_err: print("Unexpected end of file ...")
                raise Exception()
            elif tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT:
                cases: list[Case] = self.parse_cases()
                cases.insert(0, c)
                return cases
            else: return [c]
        else:
            if not self.suppress_err: print("Expected 'case' or 'default' in switch block")
            raise Exception()
    
    def parse_case(self) -> Case:
        '''
        Case : CASE Expression COLON CaseBody
        '''
        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.CASE:
            if not self.suppress_err: print("Case missing 'case' keyword")
            raise Exception()
        
        val: Expression = self.parse_expression()

        tok: Token = self.lexer.next_token()
        if tok is None or not tok.type == Token.TokenType.COLON:
            if not self.suppress_err: print("Case missing colon ':'")
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
            if not self.suppress_err: print("Reached end of program unexpectedly ...")
            raise Exception()
        elif isDefault:
            if tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT:
                if not self.suppress_err: print("'default' must be final case in switch block!")
                raise Exception()
            elif tok.type == Token.TokenType.RBRACE: return CaseBody([])
        elif tok.type == Token.TokenType.CASE or tok.type == Token.TokenType.DEFAULT: return None # Next case is coming up

        if tok.type == Token.TokenType.BREAK:
            self.lexer.pop_token()
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.SEMICOLON:
                if not self.suppress_err: print("Expected semicolon ';' after break statement")
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
            if not self.suppress_err: print("Reached unexpected end of file ...")
            raise Exception()
        
        conditions = []
        ops = []
        while tok is not None:
            if tok.type == Token.TokenType.LPAREN:
                self.lexer.pop_token()
                conditions.append(self.parse_conditions())
                self.lexer.pop_token()
            else:
                conditions.append(self.parse_condition())
        
            tok: Token = self.lexer.peek_next()
            if tok is None or not (tok.type == Token.TokenType.AND or tok.type == Token.TokenType.OR): return Conditions(conditions, ops)
            ops.append(tok.type == Token.TokenType.AND)
            self.lexer.pop_token()

            tok: Token = self.lexer.peek_next()
                
        if not self.suppress_err: print("Reached unexpected end of file ...")
        raise Exception()

    def parse_condition(self) -> Conditions:
        '''
        Condition : Expression (LT|LEQ|GT|GEQ|NEQ|EQ) Expression
                    | NOT LPAREN Expression (LT|LEQ|GT|GEQ|NEQ|EQ) Expression RPAREN
        '''
        if self.debug_mode: print("Condition")

        # Check negation
        is_negated = False
        toks: list[Token] = self.lexer.peek_tokens(2)
        if toks[0] is not None and toks[0].type == Token.TokenType.NOT:
            if toks[1] is not None and toks[1].type == Token.TokenType.LPAREN:
                self.lexer.pop_tokens(2)
                is_negated = True
            else:
                if not self.suppress_err: print("Expected '(' after '!' in condition ...")
                raise Exception()

        left = self.parse_expression()

        tok: Token = self.lexer.next_token()
        
        cond_op = None
        for op in ConditionOperation:
            if tok.content == op.value:
                cond_op = op
                break

        if cond_op is None:
            if not self.suppress_err: print(f"Invalid condition operation: {tok.content}")
            raise Exception()

        right = self.parse_expression()

        if is_negated:
            tok: Token = self.lexer.next_token()
            if tok is None or not tok.type == Token.TokenType.RPAREN:
                if not self.suppress_err: print("Missing ')' after NOT in condition")
                raise Exception()

        return Condition(left, right, op, is_negated)
    
    def parse_variable_update(self, member_access: MemberAccess|None = None):
        '''
        VariableUpdate : IDENTIFIER (ADD|SUB|MULT|DIV|MOD|BIT_AND|BIT_OR|BIT_NOT|BIT_XOR|BIT_LSHIFT|BIT_RSHIFT|empty) SET Expression
                        | INC IDENTIFIER
                        | DEC IDENTIFIER
                        | IDENTIFIER INC
                        | IDENTIFIER DEC
        '''
        tok: Token = self.lexer.peek_next()
        if tok is None:
            if not self.suppress_err: print("Unexpected end of file ...")
            raise Exception()
        
        if tok.type == Token.TokenType.INC or tok.type == Token.TokenType.DEC:
            toktype = tok.type
            self.lexer.pop_token()
            if member_access is None: member_access = self.parse_member_access()

            if toktype == Token.TokenType.INC: return VariableUpdate(member_access, VariableSetOperation.INC, None, member_access.accesses[-1].pos)
            else: return VariableUpdate(member_access, VariableSetOperation.DEC, None, member_access.accesses[-1].pos)
        else:
            if member_access is None: member_access = self.parse_member_access()

            tok: Token = self.lexer.next_token()
            if tok == Token.TokenType.INC: return VariableUpdate(member_access, VariableSetOperation.INC, None, member_access.accesses[-1].pos)
            elif tok == Token.TokenType.DEC: return VariableUpdate(member_access, VariableSetOperation.DEC, None, member_access.accesses[-1].pos)

            for op in VariableSetOperation:
                if tok.content == op.value:
                    return VariableUpdate(member_access, op, self.parse_expression(), member_access.accesses[-1].pos)

            if not self.suppress_err: print(f"Unrecognized operation: {tok.content}")
            raise Exception()
        