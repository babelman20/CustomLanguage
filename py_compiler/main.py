from core_elements import Program
from lexer import Lexer
from parser import Parser
from compiler import Compiler

if __name__ == '__main__':
    file = open('testfile.lang')
    content: str = file.read().strip()
    file.close()

    lex = Lexer(content)
    
    parser = Parser(lex)
    program: Program = parser.parse()

    compiler = Compiler(program, 'testfile', True)
    compiler.compile()