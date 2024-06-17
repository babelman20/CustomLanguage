from core_elements import *

class Compiler:

    def __init__(self, program: Program, filename: str, debug_mode: bool = False):
        self.program: Program = program
        self.filename = filename
        self.debug_mode: bool = debug_mode

    def compile(self):
        print("Start compiling")
        with open(self.filename+'.s', 'w') as file:
            self.build_readonly_data_section(file)

            self.build_data_section(file)

    # Insert immutable, static, member variables
    def build_readonly_data_section(self, file):
        file.write('.section .rodata\n')
        for var in self.program.klass.body.member_vars:
            if 'static' in var.mods and 'mut' not in var.mods:
                if 'public' in var.mods: file.write(f'\t.globl {var.name}\n')
                if var.init_val is None:
                    print(f"Immutable variable {var.name} must be initialized")
                file.write(f'\t{var.name}:\n\t\t')

                var_reserve_size = var.get_reserve_size()
                if var_reserve_size == 1: file.write('.byte')
                elif var_reserve_size == 2: file.write('.short')
                elif var_reserve_size == 4: file.write('.int')
                elif var_reserve_size == 8: file.write('.quad')
                else:
                    print(f"Unhandled reserve size {var_reserve_size}")
                    raise Exception()
                file.write(f' {var.init_val.evaluate()}\n\n')

    # Insert mutable, static, member variables
    def build_data_section(self, file):
        file.write('.section .data\n')
        for var in self.program.klass.body.member_vars:
            if 'static' in var.mods and 'mut' in var.mods:
                if 'public' in var.mods: file.write(f'\t.globl {var.name}\n')
                file.write(f'\t{var.name}:\n\t\t')

                var_reserve_size = var.get_reserve_size()
                if var.init_val is None: file.write(f'.space {var_reserve_size}')
                else:
                    if var_reserve_size == 1: file.write('.byte')
                    elif var_reserve_size == 2: file.write('.short')
                    elif var_reserve_size == 4: file.write('.int')
                    elif var_reserve_size == 8: file.write('.quad')
                    else:
                        print(f"Unhandled reserve size {var_reserve_size}")
                        raise Exception()
                    file.write(f' {var.init_val.evaluate()}\n\n')
