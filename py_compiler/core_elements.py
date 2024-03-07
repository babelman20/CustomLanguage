from enum import Enum

class Type(Enum):
    u8 = 1      # U-Byte
    u16 = 2     # U-Short
    u32 = 3     # U-Int
    u64 = 4     # U-Long

    i8 = 5      # Byte
    i16 = 6     # Short
    i32 = 7     # Int
    i64 = 8     # Long

    f32 = 9     # Float
    f64 = 10    # Double

class Variable:
    def __init__(self, public: bool, static: bool, mutable: bool, type: Type, name:str, init_val = None):
        self.public: bool = public
        self.static: bool = static
        self.mutable: bool = mutable
        self.type: Type = type
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
        output += f"{self.type.name.lower()} {self.name}"
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
        output = "}\n"
        return output

class Constructor:
    def __init__(self, public: bool, params: list[Variable], body: FunctionBody):
        self.public: bool = public
        self.params: list[Variable] = params
        self.body: FunctionBody = body

    def __str__(self) -> str:
        output = ''
        if self.public:
            output += "public "
        output += f" constructor("
        if len(self.params) > 0:
            for i in range(len(self.params)-1):
                output += f'{str(self.params[i])}, '
            output += f'{str(self.params[-1])})'
        output += f' {str(self.body)}'
        return output

class Function:
    def __init__(self, public: bool, static: bool, sealed: bool, abstract: bool, name: str, return_type: Type, params: list[Variable], body: FunctionBody):
        self.public: bool = public
        self.static: bool = static
        self.sealed: bool = sealed
        self.abstract: bool = abstract
        self.name: str = name
        self.return_type: Type = return_type
        self.params: list[Variable] = params
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
        
        output += f'{self.return_type.name.lower()} func {self.name}('
        if len(self.params) > 0:
            for i in range(len(self.params)-1):
                output += f'{str(self.params[i])}, '
            output += str(self.params[-1])
        output += f') {str(self.body)}'
        return output

class Class:
    pass

class ClassBody:
    def __init__(self, constructors: list[Constructor], member_vars: list[Variable], functions: list[Function], classes: list[Class]):
        self.constructors: Constructor = constructors
        self.member_vars: list[Variable] = member_vars
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