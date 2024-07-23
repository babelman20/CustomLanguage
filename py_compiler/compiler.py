import os

from core_elements import *

class Compiler:

    def __init__(self, path: str, classes: list[Class], filenames: list[str], debug_mode: bool = False):
        self.path = path
        self.classes: list[Class] = classes
        self.filenames: list[str] = filenames
        self.depth = 0

        self.debug_mode: bool = debug_mode

    def print(self, line):
        if self.debug_mode: print(line)

    # Try to compile each class
    def compileAll(self):
        self.print("Start compiling!")
        for klass, filename in zip(self.classes, self.filenames):
            # Only compile type-defined classes as-needed for specific variable instances (i.e. make separate array<int> and array<double> classes)
            #if len(klass.typedefs) > 0: continue
            
            self.print(f"Start compiling: {os.path.join(os.path.join(self.path,'build/intermediaries'),filename)}.s")
            self.compile(klass, filename)
        self.print("Compiling complete")

    # Try to compile a given class
    def compile(self, klass: Class, filename: str):
        filepath = f"{os.path.join(os.path.join(self.path,'build/intermediaries'),filename)}.s"

        if not os.path.isfile(filepath):
            with open(filepath, 'w') as file:
                filename = filename.replace('.','_')
                self.build_imports(file)
                self.build_readonly_data_section(file, klass)
                self.build_data_section(file, klass)
                self.build_bss_section(file, klass)
                self.build_text_section(file, klass, filename)


    # Insert immutable, static, primitive member variables
    def build_readonly_data_section(self, file, klass: Class):
        self.print("Build readonly data section")
        file.write('section .rodata\n')
        self.depth += 1
        for var in klass.body.member_vars:
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
    def build_data_section(self, file, klass: Class):
        self.print("Build data section")
        file.write('section .data\n')
        self.depth += 1
        for var in klass.body.member_vars:
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
    def build_bss_section(self, file, klass: Class):
        self.print("Build bss section")
        file.write('section .bss\n')
        self.depth += 1
        for var in klass.body.member_vars:
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
    def build_text_section(self, file, klass: Class, filename: str):
        self.print("Build text section")
        file.write('section .text\n')
        self.depth += 1

        self.build_constructors(file, klass, filename)
        self.build_functions(file, klass, filename)

        self.depth -= 1

    # Insert imports from file header
    def build_imports(self, file):
        # TODO: add extern file imports
        pass

    # Set up constructor function call
    def build_constructors(self, file, klass: Class, filename: str):
        if 'abstract' in klass.mods:
            if len(klass.body.constructors) > 0:
                print(f"Abstract class is not allowed to have constructors!")
                raise Exception()
            return
        
        if len(klass.body.constructors) == 0:
            # TODO: add default constructor
            file.write('  '*self.depth + f'global {filename}_new\n')
            file.write('  '*self.depth + f'{filename}_new:\n')
            file.write('  '*(self.depth+1) + 'ret\n\n')
        else:
            for i in range(len(klass.body.constructors)):
                self.build_constructor(file, klass, filename, i)

    
    # Set up object for all constructors
    def build_constructor(self, file, klass: Class, filename: str, i: int):
        self.print(f"Build constructor '{filename}_new_{i}'")

        constructor = klass.body.constructors[i]
        file.write('  '*self.depth + f'global {filename}_new_{i}\n')
        file.write('  '*self.depth + f'{filename}_new_{i}:\n')

        self.depth += 1
        file.write('  '*self.depth + 'enter 0, 0\n')

        # TODO: allocate memory for the object using class size

        self.build_body_block(file, filename, constructor.body, None)

        # TODO: store object in rax

        file.write('\n')
        file.write('  '*self.depth + 'leave\n')
        file.write('  '*self.depth + 'ret\n\n')

        self.depth -= 1

    # Loop to add functions
    def build_functions(self, file, klass: Class, filename: str):
        for function in klass.body.functions:
            if self.debug_mode: print(f"Build function '{filename}_{function.name}'")
            if 'public' in function.mods: 
                file.write('  '*self.depth + f'global {filename}_{function.name}\n')
            file.write('  '*self.depth + f'{filename}_{function.name}:\n')
            self.depth += 1
            self.build_function_body(file, filename, function.params, function.body, function.return_type)
            file.write('\n')
            self.depth -= 1

    # Add content of each statement to function
    def build_function_body(self, file, filename: str, params: list[Variable], body: Body, return_type: str | None):
        base_depth = self.depth

        # Set up base pointer
        file.write('  '*self.depth + 'enter 0, 0\n')
        self.print(f'Return type: {return_type}')
        self.build_body_block(file, filename, body, return_type)
        file.write('\n')

        if len(body.statements) == 0 or not type(body.statements[-1]) == Return:
            file.write('  '*self.depth + 'leave\n')
            file.write('  '*self.depth + 'ret\n')

    # Generate the assembly code for each statement in the body
    def build_body_block(self, file, filename: str, body: Body, return_type: str | None):
        for statement in body.statements:
            statement = statement.statement
            self.print(f"Build statement '{type(statement)}'")
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
