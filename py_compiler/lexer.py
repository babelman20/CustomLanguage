import re

from enum import Enum

class Token:
    class TokenType(Enum):
        PUBLIC = r'public\s'
        SEALED = r'sealed\s'
        ABSTRACT = r'abstract\s'
        CLASS = r'class\s'
        EXTENDS = r'extends\s'
        STATIC = r'static\s'
        MUTABLE = r'mut\s'
        FUNCTION = r'func\s'
        CONSTRUCTOR = r'constructor\s'
        COMMENT = r'//.*\n'
        TYPE = r'[iu](8|16|32|64)|(f(32|64))'
        VAL = r'\'\\?.\'|0x[0-9A-F]{1,8}|0o[0-7]{1,22}|0b[01]{1,64}|\d+\.\d*|\d*\.\d+'
        IDENTIFIER = r'[a-zA-Z_]\w*'
        LBRACE = r'\{'
        RBRACE = r'\}'
        LPAREN = r'\('
        RPAREN = r'\)'
        SET = r'='
        ADD = r'\+'
        SUB = r'\-'
        MULT = r'\*'
        DIV = r'/'
        MOD = r'%'
        COMMA = r','
        DOT = r'\.'
        SEMICOLON = r';'
        WS = r'\s+'

    def __init__(self, type: TokenType, content: str):
        self.type: self.TokenType = type
        self.content: str = content

    def __str__(self):
        return "Token({}, '{}')".format(self.type.name, self.content)

class Lexer:
    def __init__(self, text: str):
        self.text: str = text
        self.pos: int = 0
        self.hold_tokens: list[Token] = []

    def next_token(self) -> Token:
        if len(self.hold_tokens) > 0: 
            tok: Token = self.hold_tokens.pop(0)
            self.pos += len(tok.content)
            return tok
        return self.__next_token(self.pos, False)
    
    def peek_next(self) -> Token: return self.peek_tokens(1)[0]

    def peek_tokens(self, n: int) -> list[Token]:
        tokens = []
        if len(self.hold_tokens) > 0:
            if n >= len(self.hold_tokens):
                tokens = self.hold_tokens[0:n]
                n = 0
            else:
                tokens.extend(self.hold_tokens)
                n -= len(self.hold_tokens)

        for _ in range(n):
            tokens.append(self.__next_token(self.pos, True))

        return tokens
    
    def pop_token(self) -> None:
        if len(self.hold_tokens) > 0:
            self.hold_tokens.pop(0)

    def pop_tokens(self, n: int) -> None:
        for _ in range(min(len(self.hold_tokens), n)):
            self.hold_tokens.pop(0)
    
    def __next_token(self, pos: int, peek: bool) -> Token:
        if pos >= len(self.text): return None

        match: re.Match[str] = None
        for tok in Token.TokenType.__members__.values():
            regex: re.Pattern = re.compile(tok.value)
            match = regex.match(self.text, pos)
            if match:
                pos = match.end()
                
                if tok.name == 'WS': return self.next_token()
                else: 
                    token = Token(tok, match.group().strip())
                    if peek: self.hold_tokens.append(token)
                    return token
        
        raise Exception()