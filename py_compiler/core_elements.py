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

class Parameter:
    def __init__(self, type: str, name:str):
        self.type: str = type
        self.name: str = name

    def __str__(self) -> str:
        return f'{self.type} {self.name}'

class Variable:
    def __init__(self, public: bool, static: bool, mutable: bool, type: str, name:str, init_val = None):
        self.public: bool = public
        self.static: bool = static
        self.mutable: bool = mutable
        self.type: str = type
        self.name: str = name
        self.init_val = init_val

    def __str__(self) -> str:
        output = ''
        if self.public:
            output += "public "
        if self.static:
            output += "static "
        if self.mutable:
            output += "mut "
        output += f"{self.type} {self.name}"
        if self.init_val:
            output += f" = {self.init_val}"
        return output
    
class FunctionBody:
    def __init__(self):
        # Implement Later
        pass

    def __str__(self) -> str:
        output = "{"
        # Implement Later
        output += "}\n"
        return output

class Constructor:
    def __init__(self, public: bool, params: list[Parameter], body: FunctionBody):
        self.public: bool = public
        self.params: list[Parameter] = params
        self.body: FunctionBody = body

    def __str__(self) -> str:
        output = ''
        if self.public:
            output += "public "
        output += f" constructor("
        for i in range(len(self.params)-1):
            output += f'{self.params[i]}, '
        if len(self.params) > 0: output += f'{self.params[-1]}'
        output += f') {str(self.body)}'
        return output

class Function:
    def __init__(self, public: bool, static: bool, sealed: bool, abstract: bool, name: str, return_type: str, params: list[Parameter], body: FunctionBody):
        self.public: bool = public
        self.static: bool = static
        self.sealed: bool = sealed
        self.abstract: bool = abstract
        self.name: str = name
        self.return_type: str = return_type
        self.params: list[Parameter] = params
        self.body: FunctionBody = body

    def __str__(self) -> str:
        output = ''
        if self.public:
            output += "public "
        if self.static:
            output += "static "
        if self.sealed:
            output += "sealed "
        elif self.abstract:
            output += "abstract "
        
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
        self.constructors: Constructor = constructors
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
    def __init__(self, public: bool, sealed: bool, abstract: bool, name: str, extension: str, body: ClassBody):
        self.public: bool = public
        self.sealed: bool = sealed
        self.abstract: bool = abstract
        self.name: str = name
        self.extension: str = extension
        self.body: ClassBody = body

    def __str__(self) -> str:
        output = ''
        if self.public:
            output += 'public '
        if self.sealed:
            output += 'sealed '
        elif self.abstract:
            output += 'abstract '
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