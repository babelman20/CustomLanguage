section .text

  global read
  read:
    mov rax, 0x00  ; Syscall read
    syscall
    ret

  global write
  write:
    mov rax, 0x01  ; Syscall write
    syscall
    ret

  global open
  open:
    mov rax, 0x02  ; Syscall open
    syscall
    ret

  global close
  close:
    mov rax, 0x03  ; Syscall close
    syscall
    ret

  global stat
  stat:
    mov rax, 0x04  ; Syscall stat
    syscall
    ret

  global fstat
  fstat:
    mov rax, 0x05  ; Syscall fstat
    syscall
    ret

  global brk
  brk:
    mov rax, 0x0C  ; Syscall brk
    syscall
    ret

  global exit
  exit:
    mov rax, 0x3c ; Syscall exit
    syscall

  