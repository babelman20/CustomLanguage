section .rodata
section .data
section .bss
section .text
  global customlang_utils_Syscall_read
  customlang_utils_Syscall_read:
    push rbp
    mov rbp, rsp

    mov rax, 0x00
    mov edi, [rbp+16]
    mov rsi, [rbp+20]
    mov rdx, [rbp+28]
    syscall

    mov rsp, rbp
    pop rbp
    ret

