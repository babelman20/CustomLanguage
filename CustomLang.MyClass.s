section .rodata
  global myVar
  myVar db 1

  global myVar2
  myVar2 dw 2

  myVar3 dd 3

section .data
  global myVar4
  myVar4 dq 4

  myVar5 dd 5

section .bss
  myVar6 resb 1

  global myVar8
  myVar8 resq 1

section .text
  global CustomLang_MyClass_new_0
  CustomLang_MyClass_new_0:
    ret

  global CustomLang_MyClass_myFunction1
  CustomLang_MyClass_myFunction1:


  global CustomLang_MyClass_myFunction2
  CustomLang_MyClass_myFunction2:


