# CustomLanguage

Lexer, Parser, and Compiler for my custom programming language.

This will be an object-oriented language that is highly memory efficient.  I want the majority of work to be done at compile time for fastest execution.

# Revision History

## InDev Version 0.3.0 - 2024-11-20
- Compiler Updates:
    - Added support for expression computation using operations (+,-,*,/)
    - Tracks the content of registers for optimal usage and limiting the number of load commands
    - Uses RPN to preserve operation order
    - Overhauled variable use tracking for higher efficiency
    - Added strategy to track intermediate values in expression computation

## InDev Version 0.2.11 - 2024-07-29
- Parser Updates:
    - Added end position to most statements to track when variables local to that body go out of scope
    - Fixed some variable update naming problems
- Compiler Updates:
    - Fixed variable update logic to work better with member accessing

## InDev Version 0.2.10 - 2024-07-29
- Parser Updates:
    - Fixed variable updating to allow updates to and using member variables
    - Added token position number to track variables
- Compiler Updates:
    - Implemented most of the variable tracking logic

## InDev Version 0.2.9 - 2024-07-26
- Parser Updates:
    - Added parsing for typdef in function parameters
- Compiler Updates:
    - Added tracking for local variables
    - Overhauled Environment for better variable tracking based on depth
    - Added parameter handling for constructors
    - Implemented variable declaration compiling to support all operations

## InDev Version 0.2.8 - 2024-07-24
- Added revision history and updated README
- Parser Updates:
    - Fixed another misspelling of "Statement"
- Compiler Updates:
    - Removed partially written function declaration

## InDev Version 0.2.7 - 2024-07-24
- Parser Updates:
    - Updated expressions to support function calls, object construction, and variables directly without member access wrapping
    - Fixed member access parsing to require actual access of a member (duh)
    - Added support for bitwise arithmetic in expressions
- Compiler Updates:
    - Added environments to track variables for the class and locally
    - Now preprocess class-level variables to reduce looping and create class-level environment
    - Added offset computation to track relative memory position for variables
    - Started work to compile variable updates and declarations
    - Fixed depth to update within body instead of in function/constructor initialization

## InDev Version 0.2.6 - 2024-07-23
- Wrote basic assembly code to get value from array at index
- Lexer Updates:
    - Added support for (+=, -=, *=, /=, %=) tokens
    - Added support for bit left/right shift tokens
- Parser Updates:
    - Added check for operator overloading to accomodate array brackets
    - Added support for bitwise arithmetic in expressions

## InDev Version 0.2.5 - 2024-07-23
- Wrote basic assembly code to get value from array at index
- Lexer Updates:
    - Added support for CONSTEXPR and bracket tokens
- Parser Updates:
    - Added CONSTEXPR parsing support for if blocks
- Compiler Updates:
    - Now takes all classes and packages at once instead of one at a time
    - Only compiles classes that don't have an existing assembly file

## InDev Version 0.2.4 - 2024-07-11
- Started work on an array class for the language
- Lexer Updates:
    - Added brackets to identifier token to check for array declarations
- Parser Updates:
    - Added type definition parsing with angle brackets
    - Separated constructor and function call parsing
- Compiler Updates:
    - Added frame management for constructors and functions
    - Started framework for compiling statements in function body
    - Added support for compiling ASM blocks
    - Added debugging statements

## InDev Version 0.2.3 - 2024-07-10
- Added ASM block for injecting assembly code directly into compiled file
- Changed syscall assembly file to an abstract language class file
- Lexer Updates:
    - Added support for ASM block and Quote (text) ""
- Parser Updates:
    - Added parsing for ASM blocks

## InDev Version 0.2.2 - 2024-07-09
- Created basic 'syscall' assembly code with functions for some system calls
- Tested 'brk' syscall for reserving memory

## InDev Version 0.2.1 - 2024-06-26
- Now supports parsing and compiling multiple files
- Core Element Updates:
    - Variables now have a get_reserve_size function that returns the size of the variable in bytes (8 bytes for objects)
    - Variables now have a is_primitive_type function to check if it's primitive
    - Classes now have a get_size function that returns the sum of bytes needed for its member variables
    - Program updated to contain multiple classes from multiple packages
- Parser Updates:
    - Now parses classes individually and returns a parsed class instead of 'Program' object
- Compiler Updates:
    - Fixed variables to use db/dw/dd/dq instead of byte/short/int/quad
    - Added BSS section for object variables and uninitialized primitive variables
    - Added Text section
    - Added constructor compiling and abstract class check
    - Added function compiling (not function body)

## InDev Version 0.2.0 - 2024-06-16
- Added basic compiler!  Code is compiled directly to assembly from language files
- Parser Updates:
    - Changed expression parsing from recursive to loop
    - Implemented function call, variable declaration, and variable updating parsing as body statements
- Compiler Updates:
    - Generates readonly and data sections to store static primitive variables

## InDev Version 0.1.3 - 2024-03-18
- Updated lexical rules to use word boundary instead of space
- Lexer Updates:
    - Added support for switch, foreach, break, and return statements
    - Removed left parenthesis from if/else/while/for tokens
- Parser Updates:
    - Added parsing for switch, foreach, break and return
    - Added special parsing for switch cases and case blocks
    - Corrected spelling of "Statement" from "Statment"

## InDev Version 0.1.2 - 2024-03-17
- Updated lexical rules to use word boundary instead of space
- Lexer Updates:
    - Added support for logical expressions (>, <, ==, &&, ||, etc.)
    - Added support for bitwise and/or/not/xor arithmetic
- Parser Updates:
    - Updated several parsing functions to use lexer's multi-token capability
    - Added early EOF and unexpected token checks
    - Simplified modifier parsing to use loops instead of recursion
    - Added return type to function declarations
    - Added unique parsing for constructor calls
    - Created generic body parsing for functions/constructors
    - Added parsing for statements in body including if/while/for, variable setting/declaration, and function calls
    - Added conditions parsing for if/while/for

## InDev Version 0.1.1 - 2024-03-12
- Finished previously incomplete basic lexer/parser features
- Lexer Updates:
    - Added debug mode for verbose print statements
    - Added parsing for multiple tokens and token look-ahead
    - Tokens are requested as needed instead of all being generated at once
- Parser Updates:
    - Takes Lexer as input to request next tokens
    - Simplified modifiers by combining access and special modifiers
    - Overhauled class body parsing to separate function/variable/subclass declarations
    - Added parameter parsing for constructors and functions
    - Added argument parsing for function/constructor calls
    - Now parses comments out of function body
    - Added expression parsing for evaluating arithmetic
    - Added parsing for function calls

## InDev Version 0.1.0 - 2024-03-07
- Started basic lexer and parser
- Lexer supports:
    - Modifiers for classes/functions/variables
    - Named classes/functions/variables
    - Constructors
    - Comments
    - Primitive types (u8, i8, u16, i16, u32, i32, f32, u64, i64, f64)
    - Numerical Values
    - Braces {} and parenthesis ()
    - Basic arithmetic (+, -, *, /, %)
- Parser supports:
    - Class declarations with modifiers
    - Member declarations of constructors, functions, and variables
    - Variable initialization

## InDev Version 0.0.2 - 2024-03-05
- Fixed "read_line.s" assembly code to make read/write system calls

## InDev Version 0.0.1 - 2024-03-04
- First tested running system calls in ARM assembly (read/write)
- Created first Makefile
- Started C/C++ compiler for language

## InDev Version 0.0.0 - 2024-02-27
- Initial creation of GitHub repository