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
  global myVar6
  myVar6 resq 1

  myVar8 resb 1

section .text
  global testfile_new_0
  testfile_new_0:
    push rbp
    mov rbp, rsp


    mov rsp, rbp
    pop rbp
    ret

  global testfile_myFunction1
  testfile_myFunction1:
    enter 0, 0

    leave
    ret

  global testfile_myFunction2
  testfile_myFunction2:
    enter 0, 0

    leave
    ret

