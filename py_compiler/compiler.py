import os

from core_elements import *

class ClassEnvironment:
    def __init__(self, name: str, static_imut_vars: list[Variable], static_mut_vars: list[Variable], static_vars: list[Variable], member_vars: dict[Variable, int], imports: list[Class]):
        self.name: str = name
        self.static_imut_vars: list[Variable] = static_imut_vars
        self.static_mut_vars: list[Variable] = static_mut_vars
        self.static_vars: list[Variable] = static_vars
        self.member_vars: dict[Variable, int] = member_vars  # Name/address pairs
        self.imports = imports

class LocalEnvironment:
    pass

class LocalEnvironment:
    def __init__(self, depth: int, local_vars: dict[Variable, int] = [], prevEnvs: list[LocalEnvironment] = []):
        self.depth :int = depth
        self.local_vars: dict[Variable, int] = local_vars  # Name/address pairs
        self.prevEnvs = prevEnvs

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
            self.print("Done!\n")
        self.print("Compiling complete")

    # Try to compile a given class
    def compile(self, klass: Class, filename: str):
        filepath = f"{os.path.join(os.path.join(self.path,'build/intermediaries'),filename)}.s"

        if not os.path.isfile(filepath):
            with open(filepath, 'w') as file:
                filename = filename.replace('.','_')
                self.build_imports(file)
                classEnv: ClassEnvironment = self.precompile_member_vars(klass, filename)
                self.build_readonly_data_section(file, classEnv)
                self.build_data_section(file, classEnv)
                self.build_bss_section(file, classEnv)
                self.build_text_section(file, klass, classEnv)

    def precompile_member_vars(self, klass: Class, name: str) -> ClassEnvironment:
        static_imut_vars: list[Variable] = []
        static_mut_vars: list[Variable] = []
        static_vars: list[Variable] = []
        member_vars: list[Variable] = []

        for var in klass.body.member_vars:
            if 'static' not in var.mods:  # Instance-level var
                member_vars.append(var)
            elif not var.is_primitive_type() or var.val is None: # Class-level object or uninitialized var
                    static_vars.append(var)
            elif 'mut' in var.mods:  # Mutible initialized class-level var
                static_mut_vars.append(var)
            else: # Immutible initialized class-level var
                static_imut_vars.append(var)

        offset = 8  # 8 bytes reserved for self reference
        member_var_offset_map = {}
        for var in member_vars:
            offset += var.get_reserve_size()
            member_var_offset_map[var] = offset
            self.print(f'Member var {var.name} at [self+{offset}]')

        return ClassEnvironment(name, static_imut_vars, static_mut_vars, static_vars, member_vars, [])
                

    # Insert immutable, static, primitive member variables
    def build_readonly_data_section(self, file, classEnv: ClassEnvironment):
        self.print("Build readonly data section")
        file.write('section .rodata\n')
        self.depth += 1
        for var in classEnv.static_imut_vars:
            if var.val is None:
                print(f"Immutable variable {var.name} must be initialized")
                continue

            if 'public' in var.mods: file.write('  '*self.depth + f'global {classEnv.name}_{var.name}\n')
            file.write('  '*self.depth + f'{classEnv.name}_{var.name} ')

            var_reserve_size = var.get_reserve_size()
            if var_reserve_size == 1: file.write('db')
            elif var_reserve_size == 2: file.write('dw')
            elif var_reserve_size == 4: file.write('dd')
            elif var_reserve_size == 8: file.write('dq')
            else:
                print(f"Unhandled reserve size {var_reserve_size}")
                raise Exception()
            file.write(f' {var.val.evaluate()}\n\n')
        self.depth -= 1

    # Insert mutable, static, initialized, primitive member variables
    def build_data_section(self, file, classEnv: ClassEnvironment):
        self.print("Build data section")
        file.write('section .data\n')
        self.depth += 1
        for var in classEnv.static_mut_vars:
            if 'public' in var.mods: file.write('  '*self.depth + f'global {classEnv.name}_{var.name}\n')
            file.write('  '*self.depth + f'{classEnv.name}_{var.name} ')

            var_reserve_size = var.get_reserve_size()
            if var_reserve_size == 1: file.write('db')
            elif var_reserve_size == 2: file.write('dw')
            elif var_reserve_size == 4: file.write('dd')
            elif var_reserve_size == 8: file.write('dq')
            else:
                print(f"Unhandled reserve size {var_reserve_size}")
                raise Exception()
            file.write(f' {var.val.evaluate()}\n\n')
        self.depth -= 1

    # Insert other static member variables
    def build_bss_section(self, file, classEnv: ClassEnvironment):
        self.print("Build bss section")
        file.write('section .bss\n')
        self.depth += 1
        for var in classEnv.static_vars:
            if 'public' in var.mods: file.write('  '*self.depth + f'global {classEnv.name}_{var.name}\n')
            file.write('  '*self.depth + f'{classEnv.name}_{var.name} ')

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
    def build_text_section(self, file, klass: Class, classEnv: ClassEnvironment):
        klass.body
        self.print("Build text section")
        file.write('section .text\n')
        self.depth += 1

        self.build_constructors(file, klass, classEnv)
        self.build_functions(file, klass, classEnv)

        self.depth -= 1

    # Insert imports from file header
    def build_imports(self, file):
        # TODO: add extern file imports
        pass

    # Set up constructor function call
    def build_constructors(self, file, klass: Class, classEnv: ClassEnvironment):
        if 'abstract' in klass.mods:
            if len(klass.body.constructors) > 0:
                print(f"Abstract class is not allowed to have constructors!")
                raise Exception()

        if len(klass.body.constructors) == 0: # Add default constructor
            klass.body.constructors.append(Constructor(['public'], [], Body([]))) # Empty constructor
            
        for i in range(len(klass.body.constructors)):
            self.build_constructor(file, klass, classEnv, i)

    
    # Set up object for all constructors
    def build_constructor(self, file, klass: Class, classEnv: ClassEnvironment, i: int):
        self.print(f"Build constructor '{classEnv.name}_new_{i}'")

        constructor = klass.body.constructors[i]
        file.write('  '*self.depth + f'global {classEnv.name}_new_{i}\n')
        file.write('  '*self.depth + f'{classEnv.name}_new_{i}:\n')

        
        file.write('  '*(self.depth+1) + 'enter 0, 0\n')

        # TODO: allocate memory for the object using class size

        self.build_body_block(file, classEnv, LocalEnvironment(self.depth), constructor.body, None)

        # TODO: store object in rax

        file.write('\n')
        file.write('  '*(self.depth+1) + 'leave\n')
        file.write('  '*(self.depth+1) + 'ret\n\n')

    # Loop to add functions
    def build_functions(self, file, klass: Class, classEnv: ClassEnvironment):
        for function in klass.body.functions:
            if self.debug_mode: print(f"Build function '{classEnv.name}_{function.name}'")
            if 'public' in function.mods: 
                file.write('  '*self.depth + f'global {classEnv.name}_{function.name}\n')
            file.write('  '*self.depth + f'{classEnv.name}_{function.name}:\n')

            params = function.params.copy()
            if 'static' not in function.mods:
                params.insert(0, Variable([], klass.name, klass.typedefs, 'this', None))

            self.build_function_body(file, classEnv, function.params, function.body, function.return_type)
            file.write('\n')

    # Add content of each statement to function
    def build_function_body(self, file, classEnv: ClassEnvironment, params: list[Variable], body: Body, return_type: str | None):
        offset = -16  # Address of first param
        param_addrs = {}
        for param in params:
            offset -= param.get_reserve_size()
            param_addrs[param] = offset
            self.print(f'Param: {param.name} offset [rbp+{-offset}]')

        localEnv: LocalEnvironment = LocalEnvironment(self.depth, param_addrs)

        # Set up base pointer
        file.write('  '*(self.depth+1) + 'enter 0, 0\n')
        self.print(f'Return type: {return_type}')
        self.build_body_block(file, classEnv, localEnv, body, return_type)
        file.write('\n')

        if len(body.statements) == 0 or not type(body.statements[-1]) == Return:
            file.write('  '*(self.depth+1) + 'leave\n')
            file.write('  '*(self.depth+1) + 'ret\n')

    # Generate the assembly code for each statement in the body
    def build_body_block(self, file, classEnv: ClassEnvironment, prevEnv: LocalEnvironment | None, body: Body, return_type: str | None = None):
        self.depth += 1

        if prevEnv is not None: localEnv: LocalEnvironment = LocalEnvironment(self.depth, [], [prevEnv])
        else: localEnv: LocalEnvironment = LocalEnvironment(self.depth, [], [])

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

        self.depth -= 1

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
        if statement.val is not None:
            self.print(f"Var \'{statement.name}\' has initial value \'{statement.val.evaluate()}\'")
            exp: Expression = statement.val
            for v in exp.values:
                print(f"Type: {type(v)}")
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
