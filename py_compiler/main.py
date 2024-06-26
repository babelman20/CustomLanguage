from core_elements import Program
from lexer import Lexer
from parser import Parser
from compiler import Compiler

if __name__ == '__main__':

    paths = ['CustomLang/testfile.lang']
    program: Program = Program()

    for path in paths:
        lastslash = path.rfind('/')
        pkg = path[:lastslash].replace('/','.')
        file = open(path)

        content: str = file.read().strip()
        file.close()

        lex = Lexer(content)
        
        parser = Parser(lex)
        program.add_class(parser.parse_class(), pkg)

    for i in range(program.nclasses):
        compiler = Compiler(program.classes[i], program.packages[i], True)
        compiler.compile()