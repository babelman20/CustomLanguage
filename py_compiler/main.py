from core_elements import Program
from parser import Parser
from lexer import Lexer

if __name__ == '__main__':
    file = open('testfile.lang')
    content: str = file.read().strip()
    file.close()

    lex = Lexer(content, True)
    
    parser = Parser(lex)
    program: Program = parser.parse()

    print(program)