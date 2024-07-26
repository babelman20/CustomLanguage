section .rodata
section .data
section .bss
section .text
  global customlang_utils_Syscall_new_0
  customlang_utils_Syscall_new_0:
    enter 0, 0

    leave
    ret

  global customlang_utils_Syscall_read
  customlang_utils_Syscall_read:
    enter 0, 0
    sub rsp, 4
    mov rax, 0x00
    mov edi, [rbp+16]
    mov rsi, [rbp+20]
    mov rdx, [rbp+28]
    syscall

    leave
    ret

