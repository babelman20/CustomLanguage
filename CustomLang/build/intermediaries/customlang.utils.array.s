section .rodata
section .data
section .bss
section .text
  global customlang_utils_array_new_0
  customlang_utils_array_new_0:
    enter 0, 0

    leave
    ret

  global customlang_utils_array_operator_BRACKETS
  customlang_utils_array_operator_BRACKETS:
    enter 0, 0
    sub rsp, 8
    sub rsp, 8
    mov rax, qword [rbp-8]

    leave
    ret

