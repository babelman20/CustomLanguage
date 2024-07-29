import sys
import os

from core_elements import Program
from lexer import Lexer
from parser import Parser
from compiler import Compiler

def getAllFiles(dirpath):
    file_list = []
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            file_list.append(os.path.join(root,file))
    return file_list

if __name__ == '__main__':

    args = sys.argv[1:]
    if not len(args) == 1: exit()

    dirpath = args[0]
    if not os.path.isdir(dirpath): exit()

    libs = [(f[f.find('/libs/')+6:],f) for f in getAllFiles(dirpath+'/libs')] if os.path.isdir(args[0] + '/libs') else []
    src = [(f[f.find('/src/')+5:],f) for f in getAllFiles(dirpath+'/src')] if os.path.isdir(args[0] + '/src') else []

    paths = libs + src

    print(paths)

    if not os.path.isdir(dirpath+'/build'):
        os.mkdir(dirpath+'/build')

    if not os.path.isdir(dirpath+'/build/intermediaries'):
        os.mkdir(dirpath+'/build/intermediaries')

    program: Program = Program()

    for filename, path in paths:
        lastslash = path.rfind('/')
        filename = filename.replace('/','.')
        
        if not os.path.isfile(dirpath+'/build/intermediaries/'+filename.replace('.lang','.s')):
            print("Parsing:", dirpath+'/build/intermediaries/'+filename.replace('.lang','.s'))
            file = open(path)

            content: str = file.read().strip()
            file.close()

            lex = Lexer(content, True)
            
            parser = Parser(lex)
            program.add_class(parser.parse_class(), filename.replace('.lang',''))

    compiler = Compiler(dirpath, program.classes, program.packages, True)
    compiler.compileAll()