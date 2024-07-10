import os

from core_elements import *

class Compiler:

    def __init__(self, path: str, klass: Class, filename: str, debug_mode: bool = False):
        self.path = path
        self.klass: Class = klass
        self.filename = filename
        self.depth = 0

        self.debug_mode: bool = debug_mode

    def compile(self):
        print(f"Start compiling: {os.path.join(os.path.join(self.path,'build/intermediaries'),self.filename)}.s")
        with open(f"{os.path.join(os.path.join(self.path,'build/intermediaries'),self.filename)}.s", 'w') as file:
            self.filename = self.filename.replace('.','_')
            self.build_readonly_data_section(file)
            self.build_data_section(file)
            self.build_bss_section(file)
            self.build_text_section(file)
        print("Compiling complete")

    # Insert immutable, static, primitive member variables
    def build_readonly_data_section(self, file):
        file.write('section .rodata\n')
        self.depth += 1
        for var in self.klass.body.member_vars:
            if 'static' in var.mods and 'mut' not in var.mods and var.is_primitive_type() and var.init_val is not None:
                if 'public' in var.mods: file.write('  '*self.depth + f'global {var.name}\n')
                if var.init_val is None:
                    print(f"Immutable variable {var.name} must be initialized")
                file.write('  '*self.depth + f'{var.name} ')

                var_reserve_size = var.get_reserve_size()
                if var_reserve_size == 1: file.write('db')
                elif var_reserve_size == 2: file.write('dw')
                elif var_reserve_size == 4: file.write('dd')
                elif var_reserve_size == 8: file.write('dq')
                else:
                    print(f"Unhandled reserve size {var_reserve_size}")
                    raise Exception()
                file.write(f' {var.init_val.evaluate()}\n\n')
        self.depth -= 1

    # Insert mutable, static, initialized, primitive member variables
    def build_data_section(self, file):
        file.write('section .data\n')
        self.depth += 1
        for var in self.klass.body.member_vars:
            if 'static' in var.mods and 'mut' in var.mods and var.is_primitive_type() and var.init_val is not None:
                if 'public' in var.mods: file.write('  '*self.depth + f'global {var.name}\n')
                file.write('  '*self.depth + f'{var.name} ')

                var_reserve_size = var.get_reserve_size()
                if var_reserve_size == 1: file.write('db')
                elif var_reserve_size == 2: file.write('dw')
                elif var_reserve_size == 4: file.write('dd')
                elif var_reserve_size == 8: file.write('dq')
                else:
                    print(f"Unhandled reserve size {var_reserve_size}")
                    raise Exception()
                file.write(f' {var.init_val.evaluate()}\n\n')
        self.depth -= 1

    # Insert other static member variables
    def build_bss_section(self, file):
        file.write('section .bss\n')
        self.depth += 1
        for var in self.klass.body.member_vars:
            if 'static' in var.mods and (not var.is_primitive_type() or ('mut' in var.mods and var.init_val is None)):
                if 'public' in var.mods: file.write('  '*self.depth + f'global {var.name}\n')
                file.write('  '*self.depth + f'{var.name} ')

                var_reserve_size = var.get_reserve_size()
                if var_reserve_size == 1: file.write('resb 1\n\n')
                elif var_reserve_size == 2: file.write('resw 1\n\n')
                elif var_reserve_size == 4: file.write('resd 1\n\n')
                elif var_reserve_size == 8: file.write('resq 1\n\n')
                else:
                    print(f"Unhandled reserve size {var_reserve_size}")
                    raise Exception()
        self.depth -= 1

    # Insert everything else
    def build_text_section(self, file):
        file.write('section .text\n')
        self.depth += 1

        self.build_imports(file)

        self.build_constructors(file)
        self.build_functions(file)

        self.depth -= 1

    def build_imports(self, file):
        # TODO: add extern file imports
        pass

    # Set up constructor function call
    def build_constructors(self, file):
        if 'abstract' in self.klass.mods and len(self.klass.body.constructors) > 0:
            print(f"Abstract class is not allowed to have constructors!")
            raise Exception()
        
        if len(self.klass.body.constructors) == 0:
            # TODO: add default constructor
            file.write('  '*self.depth + f'global {self.filename}_new\n')
            file.write('  '*self.depth + f'{self.filename}_new:\n')
            file.write('  '*(self.depth+1) + 'ret\n\n')
        else:
            for i in range(len(self.klass.body.constructors)):
                self.build_constructor(file, self.klass, i)

    
    # Set up object for all constructors
    def build_constructor(self, file, klass: Class, i: int):
        # TODO: allocate memory for the object using klass.size and store pointer in rax

        constructor = klass.body.constructors[i]
        file.write('  '*self.depth + f'global {self.filename}_new_{i}\n')
        file.write('  '*self.depth + f'{self.filename}_new_{i}:\n')

        self.depth += 1
        self.build_function_body(file, constructor.params, constructor.body, None)
        file.write('  '*self.depth + 'ret\n\n')
        self.depth -= 1

    def build_functions(self, file):
        for function in self.klass.body.functions:
            if 'public' in function.mods: 
                file.write('  '*self.depth + f'global {self.filename}_{function.name}\n')
            file.write('  '*self.depth + f'{self.filename}_{function.name}:\n')
            self.depth += 1
            self.build_function_body(file, function.params, function.body, function.return_type)
            file.write('\n\n')
            self.depth -= 1


    def build_function_body(self, file, params: list[Variable], body: Body, return_type: str | None):
        sp_offset = 0
        for var in params: sp_offset += var.get_reserve_size()

