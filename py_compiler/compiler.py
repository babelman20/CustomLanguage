import os

from core_elements import *

class CompiledVariable:
    def __init__(self, var: Variable, offset: int):
        self.type: str = var.type
        self.typedefs: list[str] = var.typedefs
        self.name: str = var.name
        self.offset: int = offset

    def is_primitive_type(self) -> bool:
        return self.type in primitive_types
    
    def is_signed(self) -> bool:
        return self.type in ['i8', 'i16', 'i32', 'i64']
    
    def get_reserve_size(self) -> int:
        if self.type in ['char','u8','i8']: return 1
        elif self.type in ['u16','i16']: return 2
        elif self.type in ['u32','i32','f32']: return 4
        else: return 8

class IntermediateValue:
    def __init__(self, name: str, type: str):
        self.type: str = type
        self.name: str = name
        self.offset: int = None
    
    def is_signed(self) -> bool:
        return self.type in ['i8', 'i16', 'i32', 'i64']
    
    def get_reserve_size(self) -> int:
        if self.type in ['char','u8','i8']: return 1
        elif self.type in ['u16','i16']: return 2
        elif self.type in ['u32','i32','f32']: return 4
        else: return 8

    def __str__(self): return self.name

class ClassEnvironment:
    def __init__(self, name: str, static_imut_vars: list[Variable], static_mut_vars: list[Variable], static_vars: list[Variable], member_vars: list[CompiledVariable], imports: list[Class]):
        self.name: str = name
        self.static_imut_vars: list[Variable] = static_imut_vars
        self.static_mut_vars: list[Variable] = static_mut_vars
        self.static_vars: list[Variable] = static_vars
        self.member_vars: list[CompiledVariable] = member_vars  # Variable data and offset address
        self.imports = imports

register_names = [['r8b', 'r9b', 'r10b', 'r11b', 'r12b', 'r13b', 'r14b', 'r15b'],
                  ['r8w', 'r9w', 'r10w', 'r11w', 'r12w', 'r13w', 'r14w', 'r15w'],
                  ['r8d', 'r9d', 'r10d', 'r11d', 'r12d', 'r13d', 'r14d', 'r15d'],
                  ['r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']]
class LocalEnvironment:
    def __init__(self, class_env: ClassEnvironment):
        self.class_env: ClassEnvironment = class_env
        self.vars: dict[str, CompiledVariable] = {}
        self.depth_access_locs: list[dict[str, list[int]]] = []
        self.depth_vars: list[list[CompiledVariable]] = []
        self.depth_offsets: list[int] = []
        self.depth_registers: list[list[str]] = []
        self.intermediate_values: dict[str, IntermediateValue] = {}

        self.depth_vars.append([])
        self.depth_access_locs.append({})
        self.depth_offsets.append(0)
        self.depth_registers.append([None]*len(register_names[0]))

        self.depth = 0
        
    def add_variable_reference(self, name: str, pos: int):
        if name not in self.depth_access_locs[self.depth].keys(): self.depth_access_locs[self.depth][name] = []
        self.depth_access_locs[self.depth][name].append(pos)

    def remove_variable_reference(self, name: str):
        if name in self.depth_access_locs[self.depth].keys():
            if len(self.depth_access_locs[self.depth][name]) > 0:
                del self.depth_access_locs[self.depth][name][0]

    def define_variable(self, var: Variable):
        print(f"DEFINED: {var.name}")
        self.depth_offsets[self.depth] += var.get_reserve_size()
        compiled = CompiledVariable(var, self.depth_offsets[self.depth])

        self.vars[compiled.name] = compiled
        self.depth_vars[self.depth].append(compiled)
        self.depth_access_locs[self.depth][compiled] = []

    def find_variable(self, name: str) -> CompiledVariable | None:
        if name not in self.vars.keys(): return None
        return self.vars[name]

    # Store all registers
    def new_depth(self, file):
        # file.write("sub rsp, 64\n" +
        #             "mov [rsp], r8\n" +
        #             "mov [rsp+8], r9\n" +
        #             "mov [rsp+16], r10\n" +
        #             "mov [rsp+24], r11\n" +
        #             "mov [rsp+32], r12\n" +
        #             "mov [rsp+40], r13\n" +
        #             "mov [rsp+48], r14\n" +
        #             "mov [rsp+56], r15\n\n")

        self.depth += 1
        self.depth_vars.append([])
        self.depth_access_locs.append({})
        self.depth_offsets.append(self.depth_offsets[-1]+(8*len(register_names[0])) if self.depth != 0 else 0)
        self.depth_registers.append(self.depth_registers[-1].copy() if self.depth != 0 else [None]*len(register_names[0]))
        
    # Restore all registers
    def leave_depth(self, file):
        # file.write("sub rsp, 64\n" +
        #             "mov r8, [rsp]\n" +
        #             "mov r9, [rsp+8]\n" +
        #             "mov r10, [rsp+16]\n" +
        #             "mov r11, [rsp+24]\n" +
        #             "mov r12, [rsp+32]\n" +
        #             "mov r13, [rsp+40]\n" +
        #             "mov r14, [rsp+48]\n" +
        #             "mov r15, [rsp+56]\n\n")
        
        for var in self.depth_vars[self.depth]:
            del self.vars[var.name]
        del self.depth_vars[-1]
        del self.depth_access_locs[-1]
        del self.depth_offsets[-1]
        del self.depth_registers[-1]
        self.depth -= 1

    # Gets the register name given index and variable
    def get_register_name(self, var: CompiledVariable|IntermediateValue, index: int):
        size = var.get_reserve_size()
        if size == 1: return register_names[0][index]
        elif size == 2: return register_names[1][index]
        elif size == 4: return register_names[2][index]
        else: return register_names[3][index]

    # Get the "A" register name (al, ax, eax, rax)
    def get_output_register_name(self, var: CompiledVariable|IntermediateValue):
        size = var.get_reserve_size()
        if size == 1: return 'al'
        elif size == 2: return 'ax'
        elif size == 4: return 'eax'
        else: return 'rax'

    # Add an intermediate value to be recognized by the registers
    def add_intermediate_val(self, val: IntermediateValue):
        self.intermediate_values[val.name] = val

    # Remove all intermediate values when an expresion is done computing
    def erase_intermediate_vals(self):
        self.intermediate_values.clear()

    # Returns the register to store the variable
    def get_register(self, name: str, file, file_indent: str, store_val: bool=True) -> str:
        registers = self.depth_registers[self.depth]

        if name in registers:  # Variable is already in a register
            index = registers.index(name)
            var = self.find_variable(name)
            if var is None: var = self.intermediate_values[name]
            self.depth_registers[self.depth][index] = name
            return self.get_register_name(var, index)
        
        if None in registers:  # There is an empty register
            none_index = registers.index(None)
            var = self.find_variable(name)
            if var is None: var = self.intermediate_values[name]
            self.depth_registers[self.depth][none_index] = name
            register_name = self.get_register_name(var, none_index)

            if store_val: file.write(file_indent+f"mov {register_name}, [rsp+{var.offset}]\n")
            return register_name
        
        # Find which register to pop a value from
        access_locs = self.depth_access_locs[self.depth]
        farthest_ref, farthest_index = 0, -1
        for i in range(len(register_names[0])):
            accesses = access_locs[registers[i]]
            if len(accesses) == 0:
                farthest_index = i
                break
            elif accesses[i] > farthest_ref:
                farthest_ref = accesses[i]
                farthest_index = i

        # Push intermediate calculation value on the stack
        if self.find_variable(registers[farthest_index]) is None: # Register holds intermediate calculation value
            var = self.intermediate_values[registers[farthest_index]]
            self.depth_offsets[self.depth] += var.get_reserve_size()
            var.offset = self.depth_offsets[self.depth]
            register_name = self.get_register_name(var, farthest_index)
            file.write(file_indent+f"mov [rsp+{var.offset}], {register_name}\n")
        
        # Store new variable in the register
        var = self.find_variable(name)
        if var is None: var = self.intermediate_values[name]
        register_name = self.get_register_name(var, farthest_index)

        self.depth_registers[self.depth][farthest_index] = name

        if var is not None and store_val: file.write(file_indent+f"mov {register_name}, [rsp+{var.offset}]")
        return register_name



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
        env: LocalEnvironment = LocalEnvironment(class_env)

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
            self.print(f"Build function '{classEnv.name}_{function.name}'")
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
        env: LocalEnvironment = LocalEnvironment(class_env)

        # Set up base environment for function body
        offset = -16  # Address of first param
        for param in params:
            offset -= param.get_reserve_size()
            env.add_variable_reference(CompiledVariable(param, offset), self.line)
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
    def build_body_block(self, file, env: LocalEnvironment, body: Body, return_type: str | None = None):
        self.depth += 1
        env.new_depth(file)

        # Build variable access list for the entire body block
        self.generate_variable_access_list(env, body)

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

        env.leave_depth(file)
        self.depth -= 1

    def build_if_block(self, file, env: LocalEnvironment, statement: If):
        pass
    
    def build_while_block(self, file, env: LocalEnvironment, statement: While):
        pass

    def build_for_block(self, file, env: LocalEnvironment, statement: For):
        pass

    def build_foreach_block(self, file, env: LocalEnvironment, statement: ForEach):
        pass

    def build_switch_block(self, file, env: LocalEnvironment, statement: Switch):
        pass

    def build_constructor_call_statement(self, file, env: LocalEnvironment, statement: ConstructorCall):
        pass

    def build_function_call_statement(self, file, env: LocalEnvironment, statement: FunctionCall):
        pass

    def build_variable_declaration_statement(self, file, env: LocalEnvironment, var: Variable):
        # Reserve space for variable
        file.write('  '*self.depth + f'sub rsp, {var.get_reserve_size()}\n')

        if env.find_variable(var.name) is not None: # Redeclaration of var is not allowed
            raise Exception(f"Redefinition of var \"{var.name}\" not allowed")
        else: env.define_variable(var)

        if var.val is not None:  # Variable has initial value
            self.print(f"Var \'{var.name}\' has initial value \'{var.val.evaluate()}\'")
            self.build_variable_update_statement(file, env, VariableUpdate(MemberAccess([VariableAccess(var.name, var.pos)]), VariableSetOperation.SET, var.val, var.pos))

    def build_variable_update_statement(self, file, env: LocalEnvironment, var_update: VariableUpdate):
        exp: Expression = var_update.val
        op: VariableSetOperation = var_update.op

        if op == VariableSetOperation.INC:
            exp: Expression = Expression([var_update.member_access, '1'],  [Operation.ADD])
        elif op == VariableSetOperation.DEC:
            exp: Expression = Expression([var_update.member_access, '1'],  [Operation.SUB])
        elif op == VariableSetOperation.SET_ADD:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.ADD])
        elif op == VariableSetOperation.SET_SUB:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.SUB])
        elif op == VariableSetOperation.SET_MULT:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.MULT])
        elif op == VariableSetOperation.SET_DIV:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.DIV])
        elif op == VariableSetOperation.SET_MOD:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.MOD])
        elif op == VariableSetOperation.SET_BIT_AND:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_AND])
        elif op == VariableSetOperation.SET_BIT_OR:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_OR])
        elif op == VariableSetOperation.SET_BIT_NOT:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_NOT])
        elif op == VariableSetOperation.SET_BIT_XOR:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_XOR])
        elif op == VariableSetOperation.SET_BIT_LSHIFT:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_LSHIFT])
        elif op == VariableSetOperation.SET_BIT_RSHIFT:
            exp: Expression = Expression([var_update.member_access, exp], [Operation.BIT_RSHIFT])

        # TODO: Evaluate expression and store value in variable
        self.print(f"Run expression evaluation on {exp}")
        self.build_expression_evaluation(file, env, exp)

    # Maybe store expression result in rax register?  Could provide consistency in evaluations
    def build_expression_evaluation(self, file, env: LocalEnvironment, expression: Expression):
        rpn = expression.generate_RPN()

        index = 0
        while index < len(rpn):
            while index < len(rpn) and not type(rpn[index]) == Operation: index += 1
            if index >= len(rpn): break

            v1, v2, op = rpn[index-2], rpn[index-1], rpn[index]

            # If v1&v2 are explicit values, evaluate them now
            if type(v1) == Value and type(v2) == Value:
                Variable()
                if v1.type != v2.type:  # Perform a type cast
                    pass

            if type(v1) == MemberAccess:
                # TODO: Descend member access to get variable value
                # Run function/constructors and store result in RAX, descend variables and store addresses in RAX
                # For now, we only accept a single access, i.e. local/member variable of this class
                v1 = v1.accesses[0]

            # Store variable 1 in a register
            if type(v1) == VariableAccess or type(v1) == IntermediateValue: 
                reg1 = env.get_register(v1.name, file, '  '*self.depth)
                env.remove_variable_reference(v1.name)


            if type(v2) == MemberAccess:
                # TODO: Descend member access to get variable value
                # Run function/constructors and store result in RAX, descend variables and store addresses in RAX
                # For now, we only accept a single access, i.e. local/member variable of this class
                v2 = v2.accesses[0]

            # Store variable 2 in a register
            if type(v2) == VariableAccess or type(v2) == IntermediateValue: 
                reg2 = env.get_register(v2.name, file, '  '*self.depth)
                env.remove_variable_reference(v2.name)

            
            # Find a register to store the value of the result
            intermediate_val = IntermediateValue(f"|RPN|{str(v1)}|{str(v2)}", "u32")
            env.add_intermediate_val(intermediate_val)
            result_reg = env.get_register(intermediate_val.name, file, '  '*self.depth, False)

            # Perform the operation
            if op == Operation.ADD:
                file.write('  '*self.depth + f"mov {result_reg}, {reg1}\n")
                file.write('  '*self.depth + f"add {result_reg}, {reg2}\n")
            elif op == Operation.SUB:
                file.write('  '*self.depth + f"mov {result_reg}, {reg1}\n")
                file.write('  '*self.depth + f"sub {result_reg}, {reg2}\n")
            elif op == Operation.MULT:
                output_reg = env.get_output_register_name(intermediate_val)
                file.write('  '*self.depth + f"mov {output_reg}, {reg1}\n")
                file.write('  '*self.depth + f"mul {reg2}\n")
                file.write('  '*self.depth + f"mov {result_reg}, {output_reg}\n")
            elif op == Operation.DIV:
                output_reg = env.get_output_register_name(intermediate_val)
                file.write('  '*self.depth + f"mov {output_reg}, {reg1}\n")
                file.write('  '*self.depth + f"div {reg2}\n")
                file.write('  '*self.depth + f"mov {result_reg}, {output_reg}\n")
            file.write("\n")
            file.flush()

            del rpn[index-2:index+1]
            index -= 2
            rpn.insert(index, intermediate_val)
            
        # TODO: Put the final result value in the RAX register

        # Erase intermediate values
        env.erase_intermediate_vals()
        pass

    def build_return_statement(self, file, env: LocalEnvironment, statement: Return):
        pass

    def build_break_statement(self, file, env: LocalEnvironment, statement: Break):
        pass

    def build_asm_block(self, file, statement: Asm):
        asm_lines = statement.content.strip().splitlines()[1:-1]
        
        for line in asm_lines:
            file.write('  '*self.depth + f'{line.strip()}\n')


    # def build_member_access


    def generate_variable_access_list(self, env: LocalEnvironment, body: Body):
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
                if for_statement.declaration.val is not None: self.generate_variable_access_list_from_expression(env, for_statement.declaration.val)

                # Check conditions
                self.generate_variable_access_list_from_conditions(env, for_statement.conditions)  
                
                self.depth += 1
                # Check for block
                if type(for_statement.content) == Body:  self.generate_variable_access_list(env, for_statement.content)  # Check if block
                else: self.generate_variable_access_list(env, Body([for_statement.content]))
                self.depth -= 1

                # Check variable update
                env.add_variable_reference(for_statement.update.name, for_statement.update.pos)
                self.generate_variable_access_list_from_expression(env, for_statement.update.val)
                self.depth -= 1
            elif type(statement) == ForEach:
                for_each_statement: ForEach = statement
                
                self.depth += 1

                # Check iterated var
                env.add_variable_reference(for_each_statement.iterator, for_each_statement.pos)
                
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
                # env.define_variable(var)
                if var.val is not None: self.generate_variable_access_list_from_expression(env, var.val)
            elif type(statement) == VariableUpdate:
                update: VariableUpdate = statement
                
                # Check INC/DEC updates
                if update.op == VariableSetOperation.INC:
                    update.val = Expression([update.member_access, Value('1')], [Operation.ADD])
                elif update.op == VariableSetOperation.DEC:
                    update.val = Expression([update.member_access, Value('1')], [Operation.SUB])

                # Check variable updates
                if all([type(acc) == VariableAccess for acc in update.member_access.accesses]):
                    names = []
                    for i in range(len(update.member_access.accesses)-1):
                        access: VariableAccess = update.member_access.accesses[i]
                        names.append(access.name)
                        env.add_variable_reference('_'.join(names), access.pos)
                    if update.val is not None: self.generate_variable_access_list_from_expression(env, update.val)
            elif type(statement) == Return:
                return_statement: Return = statement

                # Check return statement values
                self.generate_variable_access_list_from_expression(env, return_statement.ret_val)
            elif type(statement) == Break: pass  # IGNORED
            elif type(statement) == Asm: pass  # IGNORED

    def generate_variable_access_list_from_conditions(self, env: LocalEnvironment, conditions: Conditions):
        for condition in conditions.conditions:
            self.generate_variable_access_list_from_expression(env, condition.left)
            self.generate_variable_access_list_from_expression(env, condition.right)

    def generate_variable_access_list_from_expression(self, env: LocalEnvironment, exp: Expression):
        for val in exp.generate_RPN():
            if type(val) == VariableAccess:
                env.add_variable_reference(val.name, val.pos)
            elif type(val) == MemberAccess:
                self.generate_variable_access_list_from_member_access(env, val)

    def generate_variable_access_list_from_member_access(self, env: LocalEnvironment, member_access: MemberAccess):
        for access in member_access.accesses:
            if not type(access) == VariableAccess: return
            env.add_variable_reference(access.name, access.pos)