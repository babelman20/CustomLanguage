from enum import Enum

# Primitive types are char, u8, u16, u32, u64, i8, i16, i32, i64, f32, and f64

primitive_types = ['char', 'u8', 'u16', 'u32', 'u64', 'i8', 'i16', 'i32', 'i64', 'f32', 'f64']

class Operation(Enum):
    ADD = '+'
    SUB = '-'
    MULT = '*'
    DIV = '/'
    MOD = '%'
    BIT_AND = '&'
    BIT_OR = '|'
    BIT_XOR = '^'
    BIT_NOT = '~'
    BIT_LSHIFT = '<<'
    BIT_RSHIFT = '>>'
    BRACKETS = '[]'

    def __str__(self):
        return self.value

# Lower precedence is higher order
precedence_map: dict[Operation, int] = {
    Operation.ADD: 3,
    Operation.SUB: 3,
    Operation.MULT: 2,
    Operation.DIV: 2,
    Operation.MOD: 2,
    Operation.BIT_AND: 5,
    Operation.BIT_OR: 7,
    Operation.BIT_XOR: 6,
    Operation.BIT_NOT: 1,
    Operation.BIT_LSHIFT: 4,
    Operation.BIT_RSHIFT: 4,
    Operation.BRACKETS: 0,
}

class ConditionOperation(Enum):
    LEQ = '<='
    LT = '<'
    GEQ = '>='
    GT = '>'
    NEQ = '!='
    EQ = '=='

class VariableSetOperation(Enum):
    SET = '='
    INC = '++'
    DEC = '--'
    SET_ADD = '+='
    SET_SUB = '-='
    SET_MULT = '*='
    SET_DIV = '/='
    SET_MOD = '%='
    SET_BIT_AND = '&='
    SET_BIT_OR = '|='
    SET_BIT_XOR = '^='
    SET_BIT_NOT = '~='
    SET_BIT_LSHIFT = '<<='
    SET_BIT_RSHIFT = '>>='

all_operations = [Operation.ADD, Operation.SUB, Operation.MULT, Operation.DIV, Operation.MOD, Operation.BIT_AND, Operation.BIT_OR, Operation.BIT_XOR, Operation.BIT_NOT, Operation.BIT_LSHIFT, Operation.BIT_RSHIFT, Operation.BRACKETS,
                    ConditionOperation.LEQ, ConditionOperation.LEQ, ConditionOperation.GEQ, ConditionOperation.GT ,ConditionOperation.NEQ, ConditionOperation.EQ,
                    VariableSetOperation.SET, VariableSetOperation.INC, VariableSetOperation.DEC, VariableSetOperation.SET_ADD, VariableSetOperation.SET_SUB, VariableSetOperation.SET_MULT, VariableSetOperation.SET_MOD,
                    VariableSetOperation.SET_BIT_AND, VariableSetOperation.SET_BIT_OR, VariableSetOperation.SET_BIT_XOR, VariableSetOperation.SET_BIT_NOT, VariableSetOperation.SET_BIT_LSHIFT, VariableSetOperation.SET_BIT_RSHIFT]

expression_operations = [Operation.ADD, Operation.SUB, Operation.MULT, Operation.DIV, Operation.MOD, Operation.BIT_AND, Operation.BIT_OR, Operation.BIT_XOR, Operation.BIT_LSHIFT, Operation.BIT_RSHIFT]

class Expression:
    pass

class MemberAccess:
    pass

class ConstructorCall:
    def __init__(self, name: str, typedefs: list[str], args: list[Expression]):
        self.name = name
        self.typedefs = typedefs
        self.args = args

    def __str__(self):
        output = f"new {self.name}"
        if self.typedefs is not None and len(self.typedefs) > 0:
            output += '<'
            for i in range(len(self.typedefs)-1):
                output += f'{self.typedefs[i]}, '
            output += f'{self.typedefs[-1]}>'
        output += "("
        for i in range(len(self.args)-1):
            output += f"{self.args[i]}, "
        if len(self.args) > 0: output += str(self.args[-1])
        output += ")"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, ConstructorCall): return False
        return self.name == other.name and self.typedefs == other.typedefs and self.args == other.args


class FunctionCall:
    def __init__(self, name: str, args: list[Expression]):
        self.name = name
        self.args = args

    def __str__(self):
        output = f"{self.name}("
        for i in range(len(self.args)-1):
            output += f"{self.args[i]}, "
        if len(self.args) > 0: output += str(self.args[-1])
        output += ")"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, FunctionCall): return False
        return self.name == other.name and self.args == other.args

class Value:
    def __init__(self, val: str):
        self.val: str = val

        val = float(val)
        if int(val) == val: # Val is an integer
            signed = (val < 0)
            val = abs(val)
            if val >= 0xFFFFFF: self.type = 'i64' if signed else 'u64'
            elif val >= 0xFFFF: self.type = 'i32' if signed else 'u32'
            elif val >= 0xFF: self.type = 'i16' if signed else 'u16'
            else: self.type = 'i8' if signed else 'u8'
        else: # Val is a float
            if abs(val) < 1.4e-45 or abs(val) > 3.4e38: self.type = 'f64'
            else: self.type = 'f32'

    def __str__(self):
        return self.val
    
    def __eq__(self, other):
        if not isinstance(other, Value): return False
        return self.val == other.val

class VariableAccess:
    def __init__(self, name: str, pos: int):
        self.name: str = name
        self.pos: int = pos

    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        if not isinstance(other, VariableAccess): return False
        return self.name == other.name

class MemberAccess:
    def __init__(self, accesses: list[VariableAccess | FunctionCall | ConstructorCall]):
        self.accesses: list[VariableAccess | FunctionCall | ConstructorCall] = accesses

    def __str__(self):
        output = ''
        for i in range(len(self.accesses)-1):
            output += str(self.accesses[i]) + '.'
        output += str(self.accesses[-1])
        return output
    
    def __eq__(self, other):
        if not isinstance(other, MemberAccess): return False
        return self.accesses == other.accesses

class Expression:
    def __init__(self, values: list[Expression | MemberAccess | Value], ops: list[Operation] = []): # Val is a raw value or a function call
        if (not type(values) is list and len(ops) > 0) or (not len(values)-1 == len(ops)):
            print("Values/Operations mismatch !!!")
            raise Exception()
        self.values: list[Expression | MemberAccess | Value] = values
        self.ops: list[Operation] = ops

    def __str__(self):
        output: str = "("
        for i in range(len(self.ops)):
            output += f"{self.values[i]} {self.ops[i].value} "
        output += f"{self.values[-1]}"
        output += ")"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Expression): return False
        return self.values == other.values and self.ops == other.ops
    
    def generate_RPN(self) -> list[MemberAccess | VariableAccess | FunctionCall | ConstructorCall | Value | Operation]:
        if len(self.values) == 1: return self.values if type(self.values[0]) is not Expression else self.values[0].generate_RPN()

        if type(self.values[0]) is not Expression:
            output = [self.values[0]]   
        else:
            output = self.values[0].generate_RPN()
        op_stack = []

        index = 0
        while index < len(self.ops):
            if type(self.values[index+1]) is not Expression:
                output.append(self.values[index+1])
            else:
                output.extend(self.values[index+1].generate_RPN())
            while (op_stack and precedence_map[op_stack[-1]] <= precedence_map[self.ops[index]]):
                output.append(op_stack.pop())
            op_stack.append(self.ops[index])
            index += 1

        while op_stack:
            output.append(op_stack.pop())

        return output
    
    def evaluate(self):
        if len(self.values) == 1: return str(self.values[0])

        # TODO: Implement actual evaluation of expressions
        return str(self)


class Condition:
    def __init__(self, left: Expression, right: Expression, operation: ConditionOperation, is_negated: bool):
        self.left = left
        self.right = right
        self.operation = operation
        self.is_negated = is_negated

    def __str__(self):
       if self.is_negated: return f"!({self.left} {self.operation.value} {self.right})"
       else: return f"{self.left} {self.operation.value} {self.right}"

    def __eq__(self, other):
        if not isinstance(other, Condition): return False
        return self.left == other.left and self.right == other.right and self.operation == other.operation and self.is_negated == other.is_negated

class Conditions:
    pass

class Conditions:
    def __init__(self, conditions: list[Conditions | Condition], ops: list[bool]):  # ops[i] == True for AND, False for OR
        self.conditions = conditions
        self.ops = ops

    def __str__(self):
        output = "("
        for i in range(len(self.conditions)-1):
            output += f"{self.conditions[i]} {'&&' if self.ops[i] else '||'}"
        output += f'{self.conditions[-1]})'

    def __eq__(self, other):
        if not isinstance(other, Conditions): return False
        return self.conditions == other.conditions and self.ops == other.ops

class Parameter:
    def __init__(self, type: str, typedefs: list[str], name: str):
        self.type: str = type
        self.typedefs: list[str] = typedefs
        self.name: str = name

    def __str__(self) -> str:
        output = f'{self.type}'

        if self.typedefs is not None:
            output += '<'
            for i in range(len(self.typedefs)-1):
                output += f'{self.typedefs[i]}, '
            output += f'{self.typedefs[-1]}>'
        return f'{self.type} {self.name}'
    
    def __eq__(self, other):
        if not isinstance(other, Parameter): return False
        return self.name == other.name and self.type == other.type and self.typedefs == other.typedefs
    
    def get_reserve_size(self) -> int:
        if self.type in ['u8','i8']: return 1
        elif self.type in ['u16','i16']: return 2
        elif self.type in ['u32','i32','f32']: return 4
        else: return 8

class Variable:
    def __init__(self, mods: list[str], type: str, typedefs: list[str], name: str, pos: int, val: Expression | None = None):
        self.mods: list[str] = mods
        self.type: str = type
        self.typedefs: list[str] = typedefs
        self.name: str = name
        self.pos: int = pos
        self.val: Expression|None = val

    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        if self.type is not None:
             output += f"{self.type} "
        output += self.name
        if self.val is not None:
            output += f" = {self.val}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Variable): return False
        return self.mods == other.mods and self.type == other.type and self.typedefs == other.typedefs and self.name == other.name and self.val == other.val
    
    def is_primitive_type(self) -> bool:
        return self.type in primitive_types
    
    def is_signed(self) -> bool:
        return self.type in ['i8', 'i16', 'i32', 'i64']
    
    def get_reserve_size(self) -> int:
        if self.type in ['char','u8','i8']: return 1
        elif self.type in ['u16','i16']: return 2
        elif self.type in ['u32','i32','f32']: return 4
        else: return 8

class Statement:
    def __init__(self, statement):
        self.statement = statement

    def __str__(self) -> str:
        return f"{self.statement}"
    
    def __eq__(self, other):
        if not isinstance(other, Statement): return False
        return self.statement == other.statement

class Body:
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def __str__(self) -> str:
        output = "{\n"
        for s in self.statements:
            output += f"{s}\n"
        output += "}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Body): return False
        return self.statements == other.statements
    
class CaseBody(Body):
    def __str__(self) -> str:
        output = ""
        if len(self.statements) > 0:
            for i in range(len(self.statements)-1):
                output += f"{self.statements[i]}\n"
            output += str(self.statements[-1])
        return output
    
    def __eq__(self, other):
        if not isinstance(other, CaseBody): return False
        return super().__eq__(other)
    
class Break:
    def __str__(self) -> str:
        return "break;"
    
    def __eq__(self, other):
        return isinstance(other, Break)
    
class Return:
    def __init__(self, ret_val: Expression):
        self.ret_val = ret_val

    def __str__(self) -> str:
        if self.ret_val: return f"return {self.ret_val};"
        return "return;"
    
    def __eq__(self, other):
        if not isinstance(other, Return): return False
        return self.ret_val == other.ret_val
    
class Asm:
    def __init__(self, content: str):
        self.content = content
    
    def __str__(self) -> str:
        return "asm \{\n" + self.content + "\n}\n"
    
    def __eq__(self, other):
        if not isinstance(other, Asm): return False
        return self.content == other.content
    
class VariableUpdate:
    def __init__(self, member_access: MemberAccess, op: VariableSetOperation, val: Expression, pos: int):
        self.member_access = member_access
        self.op = op
        self.val = val
        self.pos = pos

    def __str__(self) -> str:
        if self.op == VariableSetOperation.INC: 
            if self.val: return f"++{self.member_access}"
            else: return f"{self.member_access}++"
        elif self.op == VariableSetOperation.DEC:
            if self.val: return f"--{self.member_access}"
            else: return f"{self.member_access}--"
        return f"{self.member_access} {self.op.value} {self.val}"
    
    def __eq__(self, other):
        if not isinstance(other, VariableUpdate): return False
        return self.member_access == other.member_access and self.op == other.op and self.val == other.val

class If:
    pass

class If:
    def __init__(self, constexpr: bool, conditions: Conditions, content: Statement | Body, elseifs: list[If], els: Statement | Body, end_pos: int):
        self.constexpr = constexpr
        self.conditions = conditions
        self.content = content
        self.elseifs = elseifs
        self.els = els
        self.end_pos = end_pos

    def __str__(self) -> str:
        output = f"if ({self.conditions}) "
        output += f"{self.content}"
        if type(self.content) == Statement: output += '\n'
        else: output += ' '
        if len(self.elseifs) > 0:
            for elseif in self.elseifs:
                output += f"else {elseif}"
        if not self.els is None: 
            output += f"else {self.els}"
            if type(self.els) == Statement: output += '\n'
 
        return output
    
    def __eq__(self, other):
        if not isinstance(other, If): return False
        return self.constexpr == other.constexpr and self.conditions == other.conditions \
            and self.content == other.content and self.elseifs == other.elseifs and self.els == other.els

class While:
    def __init__(self, conditions: Conditions, content: Statement | Body, end_pos: int):
        self.conditions = conditions
        self.content = content
        self.end_pos = end_pos

    def __str__(self) -> str:
        output = f"while ({self.conditions}) "
        output += f"{self.content}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, While): return False
        return self.conditions == other.conditions and self.content == other.content
    
class For:
    def __init__(self, declaration: Variable, conditions: Conditions, update: VariableUpdate, content: Statement | Body, end_pos: int):
        self.declaration = declaration
        self.conditions = conditions
        self.update = update
        self.content = content
        self.end_pos = end_pos

    def __str__(self) -> str:
        output = f"for ({self.declaration}; {self.conditions}; {self.update}) "
        output += f"{self.content}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, For): return False
        return self.declaration == other.declaration and self.conditions == other.conditions \
                 and self.update == other.update and self.content == other.content
    
class ForEach:
    def __init__(self, var: Variable, iterator: MemberAccess, content: Statement | Body, end_pos: int):
        self.var = var
        self.iterator = iterator
        self.content = content
        self.end_pos = end_pos

    def __str__(self) -> str:
        output = f"foreach ({self.var} in {self.iterator}) "
        output += f"{self.content}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, ForEach): return False
        return self.var == other.var and self.iterator == other.iterator and self.content == other.content
    
class Case:
    def __init__(self, val: MemberAccess|Value, content: Body):
            self.val = val
            self.content = content

    def __str__(self) -> str:
        if self.val is None: return f'default:\n {self.content}'

        output = f"case {self.val}:"
        if not self.content is None: output += f"\n{self.content}"
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Case): return False
        return self.val == other.val and self.content == other.content

class Switch:
    def __init__(self, test_val: Expression, cases: list[Case]):
            self.test_val = test_val
            self.cases = cases

    def __str__(self) -> str:
        output = f"switch ({self.test_val}) " + '{\n'
        for case in self.cases:
            output += f"{case}\n"
        output += '}'
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Switch): return False
        return self.test_val == other.test_val and self.cases == other.cases

class Constructor:
    def __init__(self, mods: list[str], params: list[Parameter], body: Body):
        self.mods: list[str] = mods
        self.params: list[Parameter] = params
        self.body: Body = body

    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        output += f"constructor("
        for i in range(len(self.params)-1):
            output += f'{self.params[i]}, '
        if len(self.params) > 0: output += f'{self.params[-1]}'
        output += f') {str(self.body)}'
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Constructor): return False
        return self.mods == other.mods and self.params == other.params and self.body == other.body

class Function:
    def __init__(self, mods: list[str], name: str, return_type: str, params: list[Parameter], body: Body):
        self.mods: list[str] = mods
        self.name: str = name
        self.return_type: str = return_type
        self.params: list[Parameter] = params
        self.body: Body = body

    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        output += f'{self.return_type} func {self.name}('
        for i in range(len(self.params)-1):
            output += f'{self.params[i]}, '
        if len(self.params) > 0: output += f'{self.params[-1]}'
        output += f') {str(self.body)}'
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Function): return False
        return self.mods == other.mods and self.name == other.name and self.return_type == other.return_type \
                and self.params == other.params and self.body == other.body

class Class:
    pass

class ClassBody:
    def __init__(self, member_vars: list[Variable], constructors: list[Constructor], functions: list[Function], classes: list[Class]):
        self.member_vars: list[Variable] = member_vars
        self.constructors: list[Constructor] = constructors
        self.functions: list[Function] = functions
        self.classes: list[Class] = classes

    def __str__(self) -> str:
        output = '{\n'
        for var in self.member_vars:
            output += f'{str(var)}\n'
        output += '\n'
        for constructor in self.constructors:
            output += f'{str(constructor)}\n'
        output += '\n'
        for func in self.functions:
            output += f'{str(func)}\n'
        for c in self.classes:
            output += f'{str(c)}\n'
        output += '}\n'
        return output
    
    def __eq__(self, other):
        if not isinstance(other, ClassBody): return False
        return self.member_vars == other.member_vars and self.constructors == other.constructors \
                and self.functions == other.functions and self.classes == other.classes

class Class:
    def __init__(self, mods: list[str], name: str, typedefs: list[str], extension: str, body: ClassBody):
        self.mods: list[str] = mods
        self.name: str = name
        self.typedefs: list[str] = typedefs
        self.extension: str = extension
        self.body: ClassBody = body
        self.size = 0

    def get_size(self) -> int:
        if self.size > 0: return self.size
        self.size = 8  # Reserve space for function table pointer
        for var in self.body.member_vars:
            if 'static' not in var.mods: self.size += var.get_reserve_size()
        return self.size


    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        output += f'class {self.name}'
        if self.extension:
            output += f' extends {self.extension}'
        output += f' {self.body}'
        return output
    
    def __eq__(self, other):
        if not isinstance(other, Class): return False
        return self.mods == other.mods and self.name == other.name and self.typedefs == other.typedefs \
                and self.extension == other.extension and self.body == other.body

class Program:
    def __init__(self):
        self.nclasses = 0
        self.classes: list[Class] = []
        self.packages: list[str] = []

    def add_class(self, klass: Class, pkg: str):
        self.nclasses += 1
        self.classes.append(klass)
        self.packages.append(pkg)

    def __eq__(self, other):
        if not isinstance(other, Program): return False
        return self.classes == other.classes and self.packages == other.packages
    
    # def __str__(self) -> str:
    #     output = '\n' + str(self.klass) + '\n'
    #     return output