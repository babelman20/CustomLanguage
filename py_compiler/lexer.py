import re

from enum import Enum

class Token:
    class TokenType(Enum):
        PUBLIC = r'\bpublic\b'
        SEALED = r'\bsealed\b'
        ABSTRACT = r'\babstract\b'
        CLASS = r'\bclass\b'
        EXTENDS = r'\bextends\b'
        STATIC = r'\bstatic\b'
        MUTABLE = r'\bmut\b'
        FUNCTION = r'\bfunc\b'
        CONSTRUCTOR = r'\bconstructor\b'
        NEW = r'\bnew\b'
        ASM = r'\basm\b'
        IF = r'\bif\b'
        ELSE = r'\belse\b'
        WHILE = r'\bwhile\b'
        FOR = r'\bfor\b'
        FOREACH = r'\bforeach\b'
        IN = r'\bin\b'
        SWITCH = r'\bswitch\b'
        CASE = r'\bcase\b'
        DEFAULT = r'\bdefault\b'
        BREAK = r'\bbreak\b'
        RETURN = r'\breturn\b'
        COMMENT = r'//.*\n|/\*.*\*/'
        VAL = r'\'\\?.\'|0x[0-9A-Fa-f]{1,8}\b|0o[0-7]{1,22}\b|0b[01]{1,64}\b|\d+\.\d*\b|\d*\.\d+\b|\d+\b'
        IDENTIFIER = r'[a-zA-Z_]\w*(\[\])?'
        QUOTE = r'\"[^\"]*\"'
        LBRACE = r'{'
        RBRACE = r'}'
        LPAREN = r'\('
        RPAREN = r'\)'
        LEQ = r'<='
        LT = r'<'
        GEQ = r'>='
        GT = r'>'
        NEQ = r'!='
        EQ = r'=='
        NOT = r'!'
        AND = r'&&'
        OR = r'\|\|'
        SET = r'='
        INC = r'\+\+'
        DEC = r'\-\-'
        ADD = r'\+'
        SUB = r'\-'
        MULT = r'\*'
        DIV = r'/'
        MOD = r'%'
        BIT_AND = r'&'
        BIT_OR = r'\|'
        BIT_XOR = r'\^'
        BIT_NOT = r'~'
        COMMA = r','
        DOT = r'\.'
        COLON = r':'
        SEMICOLON = r';'
        WS = r'\s+'

    def __init__(self, type: TokenType, content: str):
        self.type: self.TokenType = type
        self.content: str = content

    def __str__(self):
        return "Token({}, '{}')".format(self.type.name, self.content)

class Lexer:
    def __init__(self, text: str, debug_mode: bool = False):
        self.text: str = text
        self.pos: int = 0
        self.hold_tokens: list[tuple[Token,int]] = []

        self.debug_mode: bool = debug_mode

        self.MODS = [Token.TokenType.PUBLIC,
                        Token.TokenType.SEALED,
                        Token.TokenType.ABSTRACT,
                        Token.TokenType.STATIC,
                        Token.TokenType.MUTABLE]

    def next_token(self) -> Token:
        if len(self.hold_tokens) > 0: 
            tok: Token = self.hold_tokens.pop(0)[0]
            return tok
        return self.__next_token(False)
    
    def next_tokens(self, n: int) -> list[Token]:
        tokens = []
        if len(self.hold_tokens) > 0: 
            if n >= len(self.hold_tokens):
                n -= len(self.hold_tokens)
                tokens = [tok[0] for tok in self.hold_tokens]
                self.hold_tokens = []
            else:
                tokens = [tok[0] for tok in self.hold_tokens[0:n]]
                del self.hold_tokens[0:n]
                return tokens
        
        for _ in range(n):
            tokens.append(self.__next_token(False))
        return tokens
    
    def peek_next(self) -> Token: return self.peek_tokens(1)[0]

    def peek_tokens(self, n: int) -> list[Token]:
        tokens = []
        if len(self.hold_tokens) > 0:
            if n >= len(self.hold_tokens):
                tokens = [tok[0] for tok in self.hold_tokens]
                n -= len(self.hold_tokens)
            else:
                return [tok[0] for tok in self.hold_tokens[0:n]]

        for _ in range(n):
            tokens.append(self.__next_token(True))

        return tokens
    
    def pop_token(self) -> None:
        if len(self.hold_tokens) > 0:
            self.hold_tokens.pop(0)

    def pop_tokens(self, n: int) -> None:
        for _ in range(min(len(self.hold_tokens), n)):
            self.hold_tokens.pop(0)
    
    def __next_token(self, peek: bool) -> Token:
        if self.pos >= len(self.text): return None

        match: re.Match[str] = None
        for tok in Token.TokenType.__members__.values():
            regex: re.Pattern = re.compile(tok.value)
            match = regex.match(self.text, self.pos)
            if match:
                self.pos = match.end()                
                if tok == Token.TokenType.WS or tok == Token.TokenType.COMMENT: return self.__next_token(peek)
                else: 
                    token = Token(tok, match.group().strip())
                    if self.debug_mode: print(f"NEXT: {tok.name} {token.content} {self.pos}")
                    if peek: self.hold_tokens.append((token,self.pos))
                    return token
        
        print("Unexpected end of file")
        raise Exception()