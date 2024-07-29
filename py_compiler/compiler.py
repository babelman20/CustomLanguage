import os

from core_elements import *

class CompiledVariable:
    def __init__(self, var: Variable, offset: int):
        self.type: str = var.type
        self.typedefs: list[str] = var.typedefs
        self.name: str = var.name
        self.offset: int = offset

class ClassEnvironment:
    def __init__(self, name: str, static_imut_vars: list[Variable], static_mut_vars: list[Variable], static_vars: list[Variable], member_vars: list[CompiledVariable], imports: list[Class]):
        self.name: str = name
        self.static_imut_vars: list[Variable] = static_imut_vars
        self.static_mut_vars: list[Variable] = static_mut_vars
        self.static_vars: list[Variable] = static_vars
        self.member_vars: list[CompiledVariable] = member_vars  # Variable data and offset address
        self.imports = imports

class Registers:
    def __init__(self):
        # Contains register name & variable name pairs
        self.registers: dict[str, str] = { 
            'rax': None,
            'rbx': None,
            'rcx': None,
            'rdx': None,
            'r8': None,
            'r9': None,
            'r10': None,
            'r11': None,
            'r12': None,
            'r13': None,
            'r14': None,
            'r15': None
        }  

    def get_register(self):
        # TODO: Add logic to find the register holding the value whose next use is the furthest away
        pass

class Environment:
    def __init__(self, class_env: ClassEnvironment):
        self.class_env: ClassEnvironment = class_env
        self.var_name_to_compiled_map: dict[str, CompiledVariable] = {}
        self.depth_map: dict[str, dict[int, list[int]]] = {}  # Map for compiled variables: tracks statement reference locations and depths
        self.offsets: dict[int, int] = {1: 0}  # Offset map for each depth
    
    def add_variable_declaration(self, var: Variable, depth: int):
        print(f"DEPTH::  {depth}")
        if depth not in self.offsets.keys(): self.offsets[depth] = self.offsets[depth-1]
        self.offsets[depth] += var.get_reserve_size()

        comp_var: CompiledVariable = CompiledVariable(var, self.offsets[depth])
        self.var_name_to_compiled_map[comp_var.name] = comp_var

    def add_variable_reference(self, var: CompiledVariable | str, depth: int, pos: int):
        if type(var) == CompiledVariable: name = var.name
        else: name = var

        if name not in self.depth_map.keys():
            self.depth_map[name] = {}
        
        if depth not in self.depth_map[name].keys():
            self.depth_map[name][depth] = []

        self.depth_map[name][depth].append(pos)

    def find_variable(self, name: str) -> CompiledVariable | None:
        for var in self.depth_map.keys():
            if name == var: return var
        return None

class Compiler:

    def __init__(self, path: str, classes: list[Class], filenames: list[str], debug_mode: bool = False):
        self.path = path
        self.classes: list[Class] = classes
        self.filenames: list[str] = filenames
        self.depth = 0
        self.line = 0

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
                class_env: ClassEnvironment = self.precompile_member_vars(klass, filename)
                self.build_readonly_data_section(file, class_env)
                self.build_data_section(file, class_env)
                self.build_bss_section(file, class_env)
                self.build_text_section(file, klass, class_env)

    def precompile_member_vars(self, klass: Class, name: str) -> ClassEnvironment:
        static_imut_vars: list[Variable] = []
        static_mut_vars: list[Variable] = []
        static_vars: list[Variable] = []
        member_vars: list[CompiledVariable] = []

        offset = 0  # 8 bytes may need to be reserved for self reference ???
        for var in klass.body.member_vars:
            if 'static' not in var.mods:  # Instance-level var
                offset += var.get_reserve_size()
                member_vars.append(CompiledVariable(var, offset))
                self.print(f'Member var {var.name} at [self+{offset}]')
            elif not var.is_primitive_type() or var.val is None: # Class-level object or uninitialized var
                    static_vars.append(var)
            elif 'mut' in var.mods:  # Mutible initialized class-level var
                static_mut_vars.append(var)
            else: # Immutible initialized class-level var
                static_imut_vars.append(var)

        return ClassEnvironment(name, static_imut_vars, static_mut_vars, static_vars, member_vars, [])
                

    # Insert immutable, static, primitive member variables
    def build_readonly_data_section(self, file, class_env: ClassEnvironment):
        self.print("Build readonly data section")
        file.write('section .rodata\n')
        self.depth += 1
        for var in class_env.static_imut_vars:
            if var.val is None:
                print(f"Immutable variable {var.name} must be initialized")
                continue

            if 'public' in var.mods: file.write('  '*self.depth + f'global {class_env.name}_{var.name}\n')
            file.write('  '*self.depth + f'{class_env.name}_{var.name} ')

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
    def build_data_section(self, file, class_env: ClassEnvironment):
        self.print("Build data section")
        file.write('section .data\n')
        self.depth += 1
        for var in class_env.static_mut_vars:
            if 'public' in var.mods: file.write('  '*self.depth + f'global {class_env.name}_{var.name}\n')
            file.write('  '*self.depth + f'{class_env.name}_{var.name} ')

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
    def build_bss_section(self, file, class_env: ClassEnvironment):
        self.print("Build bss section")
        file.write('section .bss\n')
        self.depth += 1
        for var in class_env.static_vars:
            if 'public' in var.mods: file.write('  '*self.depth + f'global {class_env.name}_{var.name}\n')
            file.write('  '*self.depth + f'{class_env.name}_{var.name} ')

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
    def build_text_section(self, file, klass: Class, class_env: ClassEnvironment):
        klass.body
        self.print("Build text section")
        file.write('section .text\n')
        self.depth += 1

        self.build_constructors(file, klass, class_env)
        self.build_functions(file, klass, class_env)

        self.depth -= 1

    # Insert imports from file header
    def build_imports(self, file):
        # TODO: add extern file imports
        pass

    # Set up constructor function call
    def build_constructors(self, file, klass: Class, class_env: ClassEnvironment):
        if 'abstract' in klass.mods:
            if len(klass.body.constructors) > 0:
                print(f"Abstract class is not allowed to have constructors!")
                raise Exception()

        if len(klass.body.constructors) == 0: # Add default constructor
            klass.body.constructors.append(Constructor(['public'], [], Body([]))) # Empty constructor
            
        for i in range(len(klass.body.constructors)):
            self.build_constructor(file, klass, class_env, i)

    
    # Set up object for all constructors
    def build_constructor(self, file, klass: Class, class_env: ClassEnvironment, i: int):
        self.print(f"Build constructor '{class_env.name}_new_{i}'")

        constructor = klass.body.constructors[i]
        file.write('  '*self.depth + f'global {class_env.name}_new_{i}\n')
        file.write('  '*self.depth + f'{class_env.name}_new_{i}:\n')

        self.line = 0
        env: Environment = Environment(class_env)

        # Set up base environment for constructor body
        offset = -16  # Address of first param
        for param in constructor.params:
            offset -= param.get_reserve_size()
            env.add_variable_reference(CompiledVariable(param, offset), self.depth, self.line)
            self.print(f'Param: {param.name} offset [rbp+{-offset}]')
        
        file.write('  '*(self.depth+1) + 'enter 0, 0\n')

        # TODO: allocate memory for the object using class size

        self.build_body_block(file, env, constructor.body, None)

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
    def build_function_body(self, file, class_env: ClassEnvironment, params: list[Variable], body: Body, return_type: str | None):
        self.line = 0
        env: Environment = Environment(class_env)

        # Set up base environment for function body
        offset = -16  # Address of first param
        for param in params:
            offset -= param.get_reserve_size()
            env.add_variable_reference(CompiledVariable(param, offset), self.depth, self.line)
            self.print(f'Param: {param.name} offset [rbp+{-offset}]')

        # Set up base pointer
        file.write('  '*(self.depth+1) + 'enter 0, 0\n')
        self.print(f'Return type: {return_type}')
        self.build_body_block(file, env, body, return_type)
        file.write('\n')

        if len(body.statements) == 0 or not type(body.statements[-1]) == Return:
            file.write('  '*(self.depth+1) + 'leave\n')
            file.write('  '*(self.depth+1) + 'ret\n')

    # Generate the assembly code for each statement in the body
    def build_body_block(self, file, env: Environment, body: Body, return_type: str | None = None):
        self.depth += 1

        # Build variable access list for the entire body block
        self.generate_variable_access_list(env, body)

        self.print('\n\n\n')
        for name in  env.depth_map.keys():
            self.print(name)
            for depth in env.depth_map[name].keys():
                self.print(f'--{depth}')
                for pos in env.depth_map[name][depth]:
                    self.print(f'----{pos}')
        self.print('\n\n\n')

        for statement in body.statements:
            self.line += 1
            statement = statement.statement
            self.print(f"Build statement '{type(statement)}' --- line {self.line}")
            if type(statement) == If:
                self.build_if_block(file, env, statement)
            elif type(statement) == While:
                self.build_while_block(file, env, statement)
            elif type(statement) == For:
                self.build_for_block(file, env, statement)
            elif type(statement) == ForEach:
                self.build_foreach_block(file, env, statement)
            elif type(statement) == Switch:
                self.build_switch_block(file, env, statement)
            elif type(statement) == FunctionCall:
                self.build_function_call_statement(file, env, statement)
            elif type(statement) == Variable:
                self.build_variable_declaration_statement(file, env, statement)
            elif type(statement) == VariableUpdate:
                self.build_variable_update_statement(file, env, statement)
            elif type(statement) == Return:
                self.build_return_statement(file, env, statement)
            elif type(statement) == Break:
                self.build_break_statement(file, env, statement)
            elif type(statement) == Asm:
                self.build_asm_block(file, statement)

        self.depth -= 1

    def build_if_block(self, file, env: Environment, statement: If):
        pass
    
    def build_while_block(self, file, env: Environment, statement: While):
        pass

    def build_for_block(self, file, env: Environment, statement: For):
        pass

    def build_foreach_block(self, file, env: Environment, statement: ForEach):
        pass

    def build_switch_block(self, file, env: Environment, statement: Switch):
        pass

    def build_constructor_call_statement(self, file, env: Environment, statement: ConstructorCall):
        pass

    def build_function_call_statement(self, file, env: Environment, statement: FunctionCall):
        pass

    def build_variable_declaration_statement(self, file, env: Environment, var: Variable):
        # Reserve space for variable
        file.write('  '*self.depth + f'sub rsp, {var.get_reserve_size()}\n')

        if var.val is not None:  # Variable has initial value
            self.print(f"Var \'{var.name}\' has initial value \'{var.val.evaluate()}\'")
            self.build_variable_update_statement(file, env, VariableUpdate(MemberAccess([VariableAccess(var.name, var.pos)]), VariableSetOperation.SET, var.val, var.pos))

    def build_variable_update_statement(self, file, env: Environment, var_update: VariableUpdate):
        exp: Expression = var_update.val
        op: VariableSetOperation = var_update.op

        self.print(f"Type: {type(var_update.member_access)}")
        self.print('  '.join([str(type(acc)) for acc in var_update.member_access.accesses]))

        if not all([type(acc) == VariableAccess for acc in var_update.member_access.accesses]): name = '__'
        else:  name = '_'.join([acc.name for acc in var_update.member_access.accesses])

        if op == VariableSetOperation.INC:
            exp: Expression = Expression([name, '1'],  [Operation.ADD])
        elif op == VariableSetOperation.DEC:
            exp: Expression = Expression([name, '1'],  [Operation.SUB])
        elif op == VariableSetOperation.SET_ADD:
            exp: Expression = Expression([name, exp], [Operation.ADD])
        elif op == VariableSetOperation.SET_SUB:
            exp: Expression = Expression([name, exp], [Operation.SUB])
        elif op == VariableSetOperation.SET_MULT:
            exp: Expression = Expression([name, exp], [Operation.MULT])
        elif op == VariableSetOperation.SET_DIV:
            exp: Expression = Expression([name, exp], [Operation.DIV])
        elif op == VariableSetOperation.SET_MOD:
            exp: Expression = Expression([name, exp], [Operation.MOD])
        elif op == VariableSetOperation.SET_BIT_AND:
            exp: Expression = Expression([name, exp], [Operation.BIT_AND])
        elif op == VariableSetOperation.SET_BIT_OR:
            exp: Expression = Expression([name, exp], [Operation.BIT_OR])
        elif op == VariableSetOperation.SET_BIT_NOT:
            exp: Expression = Expression([name, exp], [Operation.BIT_NOT])
        elif op == VariableSetOperation.SET_BIT_XOR:
            exp: Expression = Expression([name, exp], [Operation.BIT_XOR])
        elif op == VariableSetOperation.SET_BIT_LSHIFT:
            exp: Expression = Expression([name, exp], [Operation.BIT_LSHIFT])
        elif op == VariableSetOperation.SET_BIT_RSHIFT:
            exp: Expression = Expression([name, exp], [Operation.BIT_RSHIFT])

        # TODO: Evaluate expression and store value in variable
        self.print(f'Vars: {exp.values}')
        self.print(f'Ops: {[op.value for op in exp.ops]}')

        rpn = exp.generate_RPN()
        somestr = ''
        for v in rpn:
            somestr += f'{v} '
        self.print(f"Expr expansion: {somestr}")

    # Maybe store expression result in rax register?  Could provide consistency in evaluations
    def build_expression_evaluation(self, file, env: Environment, expression: Expression):
        pass

    def build_return_statement(self, file, env: Environment, statement: Return):
        pass

    def build_break_statement(self, file, env: Environment, statement: Break):
        pass

    def build_asm_block(self, file, statement: Asm):
        asm_lines = statement.content.strip().splitlines()[1:-1]
        
        for line in asm_lines:
            file.write('  '*self.depth + f'{line.strip()}\n')


    def generate_variable_access_list(self, env: Environment, body: Body):
        for statement in body.statements:
            statement = statement.statement
            if type(statement) == If:
                if_statement: If = statement
                
                # Check conditions
                self.generate_variable_access_list_from_conditions(env, if_statement.conditions)  
                
                self.depth += 1
                # Check if block
                if type(if_statement.content) == Body:  self.generate_variable_access_list(env, if_statement.content)  # Check if block
                else: self.generate_variable_access_list(env, Body([if_statement.content]))

                # Check else if blocks
                for elseif in if_statement.elseifs:
                    if type(elseif.content) == Body:  self.generate_variable_access_list(env, elseif.content)  # Check if block
                    else: self.generate_variable_access_list(env, Body([elseif.content]))

                # Check else block
                if type(if_statement.els) == Body:  self.generate_variable_access_list(env, if_statement.els)  # Check if block
                else: self.generate_variable_access_list(env, Body([if_statement.els]))
                self.depth -= 1
            elif type(statement) == While:
                while_statement: While = statement
                
                # Check conditions
                self.generate_variable_access_list_from_conditions(env, while_statement.conditions)  
                
                self.depth += 1
                # Check while block
                if type(while_statement.content) == Body:  self.generate_variable_access_list(env, while_statement.content)  # Check if block
                else: self.generate_variable_access_list(env, Body([while_statement.content]))
                self.depth -= 1
            elif type(statement) == For:
                for_statement: For = statement
                
                self.depth += 1
                # Check declaration
                env.add_variable_declaration(for_statement.declaration, self.depth)
                if for_statement.declaration.val is not None: self.generate_variable_access_list_from_expression(env, for_statement.declaration.val)

                # Check conditions
                self.generate_variable_access_list_from_conditions(env, for_statement.conditions)  
                
                self.depth += 1
                # Check for block
                if type(for_statement.content) == Body:  self.generate_variable_access_list(env, for_statement.content)  # Check if block
                else: self.generate_variable_access_list(env, Body([for_statement.content]))
                self.depth -= 1

                # Check variable update
                env.add_variable_reference(for_statement.update.name, self.depth, for_statement.update.pos)
                self.generate_variable_access_list_from_expression(env, for_statement.update.val)
                self.depth -= 1
            elif type(statement) == ForEach:
                for_each_statement: ForEach = statement
                
                self.depth += 1
                # Check declaration
                env.add_variable_declaration(for_each_statement.var, self.depth)

                # Check iterated var
                env.add_variable_reference(for_each_statement.iterator, self.depth, for_each_statement.pos)
                
                self.depth += 1
                # Check foreach block
                if type(for_each_statement.content) == Body:  self.generate_variable_access_list(env, for_each_statement.content)  # Check if block
                else: self.generate_variable_access_list(env, Body([for_each_statement.content]))
                self.depth -= 2
            elif type(statement) == Switch:
                switch_statement: Switch = statement

                # Check switch test condition
                self.generate_variable_access_list_from_expression(switch_statement.test_val)

                # Check case blocks
                self.depth += 1
                for case in switch_statement.cases:
                    if type(case.content) == Body:  self.generate_variable_access_list(env, case.content)  # Check if block
                    else: self.generate_variable_access_list(env, Body([case.content]))
                self.depth -= 1
            elif type(statement) == FunctionCall:
                function_call: FunctionCall = statement

                # Check args
                for arg in function_call.args:
                    self.generate_variable_access_list_from_expression(env, arg)
            elif type(statement) == Variable:
                var: Variable = statement
                # Check variable declaration
                env.add_variable_declaration(var, self.depth)
                if var.val is not None: self.generate_variable_access_list_from_expression(env, var.val)
            elif type(statement) == VariableUpdate:
                update: VariableUpdate = statement

                # Check variable update
                if all([type(acc) == VariableAccess for acc in update.member_access.accesses]):
                    name = '_'.join([acc.name for acc in update.member_access.accesses])
                    env.add_variable_reference(name, self.depth, update.pos)
                    self.generate_variable_access_list_from_expression(env, update.val)
            elif type(statement) == Return:
                return_statement: Return = statement

                # Check return statement values
                self.generate_variable_access_list_from_expression(env, return_statement.ret_val)
            elif type(statement) == Break: pass  # IGNORED
            elif type(statement) == Asm: pass  # IGNORED

    def generate_variable_access_list_from_conditions(self, env: Environment, conditions: Conditions):
        for condition in conditions.conditions:
            self.generate_variable_access_list_from_expression(env, condition.left)
            self.generate_variable_access_list_from_expression(env, condition.right)

    def generate_variable_access_list_from_expression(self, env: Environment, exp: Expression):
        for val in exp.generate_RPN():
            if type(val) == VariableAccess:
                env.add_variable_reference(val.name, self.depth, val.pos)