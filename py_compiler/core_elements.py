from enum import Enum

# Primitive types are u8, u16, u32, u64, i8, i16, i32, i64, f32, and f64

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
    ADD = '+='
    SUB = '-='
    MULT = '*='
    DIV = '/='
    MOD = '%='
    BIT_AND = '&='
    BIT_OR = '|='
    BIT_XOR = '^='
    BIT_NOT = '~='

class Expression:
    pass

class MemberAccess:
    pass

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

class MemberAccess:
    def __init__(self, name: str, func: FunctionCall = None, next: MemberAccess = None): # Val is either a function, another member access, or None (representing a member variable)
        self.name = name
        self.func = func
        self.next = next

    def __str__(self):
        output = ""
        if not self.func is None: output = str(self.func)
        else: output = str(self.name)

        if not self.next is None: output += f'.{self.next}'
        return output

class Expression:
    def __init__(self, val = None, left: Expression = None, right: Expression = None, operation: Operation = None): # Val is a raw value or a function call
        self.val = val
        self.left = left
        self.right = right
        self.operation = operation

    def __str__(self):
        if not self.val is None: return str(self.val)
        else: return f"({self.left} {self.operation.value} {self.right})"

class Condition:
    def __init__(self, left: Expression, right: Expression, operation: ConditionOperation):
        self.left = left
        self.right = right
        self.operation = operation

    def __str__(self):
       return f"{self.left} {self.operation.value} {self.right}"

class Conditions:
    pass

class Conditions:
    def __init__(self, inversed: bool, isAnd: bool, val: Condition = None, left: Conditions = None, right: Conditions = None):
        self.inversed = inversed
        self.val = val
        self.left = left
        self.right = right
        self.isAnd = isAnd

    def __str__(self):
        if self.inversed:
            if not self.val is None: return f"!({self.val})"
            elif self.isAnd: return f"!({self.left} && {self.right})"
            else: return f"!({self.left} || {self.right})"
        else:
            if not self.val is None: return f"{self.val}"
            elif self.isAnd: return f"({self.left} && {self.right})"
            else: return f"({self.left} || {self.right})"

class Parameter:
    def __init__(self, type: str, name:str):
        self.type: str = type
        self.name: str = name

    def __str__(self) -> str:
        return f'{self.type} {self.name}'

class Variable:
    def __init__(self, mods: list[str], type: str, name:str, init_val: Expression):
        self.mods: list[str] = mods
        self.type: str = type
        self.name: str = name
        self.init_val = init_val

    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        output += f"{self.type} {self.name}"
        if self.init_val:
            output += f" = {self.init_val}"
        return output

class Statement:
    def __init__(self, statement):
        self.statement = statement

    def __str__(self) -> str:
        return f"{self.statement}"

class Body:
    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def __str__(self) -> str:
        output = "{\n"
        for s in self.statements:
            output += f"{s}\n"
        output += "}"
        return output
    
class CaseBody(Body):
    def __str__(self) -> str:
        output = ""
        if len(self.statements) > 0:
            for i in range(len(self.statements)-1):
                output += f"{self.statements[i]}\n"
            output += str(self.statements[-1])
        return output
    
class Break:
    def __str__(self) -> str:
        return "break;"
    
class Return:
    def __init__(self, ret_val: Expression):
        self.ret_val = ret_val

    def __str__(self) -> str:
        if self.ret_val: return f"return {self.ret_val};"
        return "return;"
    
class VariableUpdate:
    def __init__(self, name: str, op: VariableSetOperation, val: Expression):
        self.name = name
        self.op = op
        self.val = val

    def __str__(self) -> str:
        if self.op == VariableSetOperation.INC: 
            if self.val: return f"++{self.name}"
            else: return f"{self.name}++"
        elif self.op == VariableSetOperation.DEC:
            if self.val: return f"--{self.name}"
            else: return f"{self.name}--"
        return f"{self.name} {self.op.value} {self.val}"

class If:
    pass

class If:
    def __init__(self, conditions: Conditions, content: Statement | Body, elseifs: list[If], els: Statement | Body):
        self.conditions = conditions
        self.content = content
        self.elseifs = elseifs
        self.els = els

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
    
class While:
    def __init__(self, conditions: Conditions, content: Statement | Body):
        self.conditions = conditions
        self.content = content

    def __str__(self) -> str:
        output = f"while ({self.conditions}) "
        output += f"{self.content}"
        return output
    
class For:
    def __init__(self, declaration: Variable, conditions: Conditions, update: VariableUpdate, content: Statement | Body):
        self.declaration = declaration
        self.conditions = conditions
        self.update = update
        self.content = content

    def __str__(self) -> str:
        output = f"for ({self.declaration}; {self.conditions}; {self.update}) "
        output += f"{self.content}"
        return output
    
class ForEach:
    def __init__(self, var: Variable, iterator: str, content: Statement | Body):
        self.var = var
        self.iterator = iterator
        self.content = content

    def __str__(self) -> str:
        output = f"foreach ({self.var} in {self.iterator}) "
        output += f"{self.content}"
        return output
    
class Case:
    def __init__(self, val: Expression, content: Body):
            self.val = val
            self.content = content

    def __str__(self) -> str:
        if self.val is None: return f'default:\n {self.content}'

        output = f"case {self.val}:"
        if not self.content is None: output += f"\n{self.content}"
        return output

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

class Class:
    def __init__(self, mods: list[str], name: str, extension: str, body: ClassBody):
        self.member_vars: list[str] = mods
        self.name: str = name
        self.extension: str = extension
        self.body: ClassBody = body

    def __str__(self) -> str:
        output = ''
        for m in self.mods:
            output += f"{m} "
        output += f'class {self.name}'
        if self.extension:
            output += f' extends {self.extension}'
        output += f' {self.body}'
        return output

class Program:
    def __init__(self, klass: Class):
        self.klass: Class = klass
    
    def __str__(self) -> str:
        output = '\n' + str(self.klass) + '\n'
        return output