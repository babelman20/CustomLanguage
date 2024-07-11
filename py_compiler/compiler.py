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
        if self.debug_mode: print(f"Start compiling: {os.path.join(os.path.join(self.path,'build/intermediaries'),self.filename)}.s")
        with open(f"{os.path.join(os.path.join(self.path,'build/intermediaries'),self.filename)}.s", 'w') as file:
            self.filename = self.filename.replace('.','_')
            self.build_imports(file)
            self.build_readonly_data_section(file)
            self.build_data_section(file)
            self.build_bss_section(file)
            self.build_text_section(file)
        if self.debug_mode: print("Compiling complete")

    # Insert immutable, static, primitive member variables
    def build_readonly_data_section(self, file):
        if self.debug_mode: print("Build readonly data section")
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
        if self.debug_mode: print("Build data section")
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
        if self.debug_mode: print("Build bss section")
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
        if self.debug_mode: print("Build text section")
        file.write('section .text\n')
        self.depth += 1

        print(f"{self.klass.typedefs}")

        self.build_constructors(file)
        self.build_functions(file)

        self.depth -= 1

    def build_imports(self, file):
        # TODO: add extern file imports
        pass

    # Set up constructor function call
    def build_constructors(self, file):
        if 'abstract' in self.klass.mods:
            if len(self.klass.body.constructors) > 0:
                print(f"Abstract class is not allowed to have constructors!")
                raise Exception()
            return
        
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
        if self.debug_mode: print(f"Build constructor '{self.filename}_new_{i}'")

        constructor = klass.body.constructors[i]
        file.write('  '*self.depth + f'global {self.filename}_new_{i}\n')
        file.write('  '*self.depth + f'{self.filename}_new_{i}:\n')

        self.depth += 1
        file.write('  '*self.depth + 'push rbp\n')
        file.write('  '*self.depth + 'mov rbp, rsp\n\n')

        # TODO: allocate memory for the object using class size

        self.build_body_block(file, constructor.body, None)

        # TODO: store object in rax

        file.write('\n')
        file.write('  '*self.depth + 'mov rsp, rbp\n')
        file.write('  '*self.depth + 'pop rbp\n')
        file.write('  '*self.depth + 'ret\n\n')

        self.depth -= 1

    # Loop to add functions
    def build_functions(self, file):
        for function in self.klass.body.functions:
            if self.debug_mode: print(f"Build function '{self.filename}_{function.name}'")
            if 'public' in function.mods: 
                file.write('  '*self.depth + f'global {self.filename}_{function.name}\n')
            file.write('  '*self.depth + f'{self.filename}_{function.name}:\n')
            self.depth += 1
            self.build_function_body(file, function.params, function.body, function.return_type)
            file.write('\n')
            self.depth -= 1

    # Add content of each statement to function
    def build_function_body(self, file, params: list[Variable], body: Body, return_type: str | None):
        base_depth = self.depth

        print([p.type for p in params])

        # Set up base pointer
        file.write('  '*self.depth + 'push rbp\n')
        file.write('  '*self.depth + 'mov rbp, rsp\n\n')

        self.build_body_block(file, body, return_type)
        file.write('\n')

        if len(body.statements) == 0 or not type(body.statements[-1]) == Return:
            file.write('  '*self.depth + 'mov rsp, rbp\n')
            file.write('  '*self.depth + 'pop rbp\n')
            file.write('  '*self.depth + 'ret\n')

    def build_body_block(self, file, body: Body, return_type: str | None):
        for statement in body.statements:
            statement = statement.statement
            if self.debug_mode: print(f"Build statement '{type(statement)}'")
            if type(statement) == If:
                self.build_if_block(file, statement)
            elif type(statement) == While:
                self.build_while_block(file, statement)
            elif type(statement) == For:
                self.build_for_block(file, statement)
            elif type(statement) == ForEach:
                self.build_foreach_block(file, statement)
            elif type(statement) == Switch:
                self.build_switch_block(file, statement)
            elif type(statement) == FunctionCall:
                self.build_function_call_statement(file, statement)
            elif type(statement) == Variable:
                self.build_variable_declaration_statement(file, statement)
            elif type(statement) == VariableUpdate:
                self.build_variable_update_statement(file, statement)
            elif type(statement) == Return:
                self.build_return_statement(file, statement)
            elif type(statement) == Break:
                self.build_break_statement(file, statement)
            elif type(statement) == Asm:
                self.build_asm_block(file, statement)

    def build_if_block(self, file, statement: If):
        pass
    
    def build_while_block(self, file, statement: While):
        pass

    def build_for_block(self, file, statement: For):
        pass

    def build_foreach_block(self, file, statement: ForEach):
        pass

    def build_switch_block(self, file, statement: Switch):
        pass

    def build_constructor_call_statement(self, file, statement: ConstructorCall):
        pass

    def build_function_call_statement(self, file, statement: FunctionCall):
        pass

    def build_variable_declaration_statement(self, file, statement: Variable):
        pass

    def build_variable_update_statement(self, file, statement: VariableUpdate):
        pass

    def build_return_statement(self, file, statement: Return):
        pass

    def build_break_statement(self, file, statement: Break):
        pass

    def build_asm_block(self, file, statement: Asm):
        asm_lines = statement.content.strip().splitlines()[1:-1]
        
        for line in asm_lines:
            file.write('  '*self.depth + f'{line.strip()}\n')
