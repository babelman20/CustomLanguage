section .rodata
  global testfile_myVar
  testfile_myVar db 1

  global testfile_myVar2
  testfile_myVar2 dw 2

  testfile_myVar3 dd 3

section .data
  global testfile_myVar4
  testfile_myVar4 dq 4

  testfile_myVar5 dd 5

section .bss
  global testfile_myVar6
  testfile_myVar6 resq 1

  testfile_myVar8 resb 1

section .text
  global testfile_new_0
  testfile_new_0:
    enter 0, 0

    leave
    ret

  global testfile_myFunction1
  testfile_myFunction1:
    enter 0, 0

    leave
    ret

  global testfile_myFunction2
  testfile_myFunction2:
    enter 0, 0
    sub rsp, 4
    sub rsp, 4
    sub rsp, 4
    sub rsp, 4
    
    mov r8d, [rsp+72]
    mov r9d, [rsp+76]
    mov r10d, r8d
    add r10d, r9d

    mov r11d, [rsp+68]
    mov eax, r11d
    mul r10d
    mov r12d, eax


    leave
    ret

