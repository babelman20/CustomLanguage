extern brk, exit

global _start
_start:
  xor rdi, rdi
  call brk

  add rax, 1024*1024
  mov rdi, rax
  call brk

  cmp rax, 0
  je brk_success
  jmp error_handling

  brk_success:
    xor rdi, rdi
    call exit

  error_handling:
    mov rdi, -1
    call exit
      