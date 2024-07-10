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
  myVar6 resq 1

  global myVar8
  myVar8 resb 1

section .text
  global testfile_new_0
  testfile_new_0:
    ret

  global testfile_myFunction1
  testfile_myFunction1:


  global testfile_myFunction2
  testfile_myFunction2:


