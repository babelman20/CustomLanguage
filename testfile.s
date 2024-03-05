section .data
    hello db 'Hello, World!',10,0    ; The string to print, null-terminated
    helloLen equ $ - hello

section .text
    global _start                  ; Linker needs this to find the entry point

_start:
    mov edx, helloLen                    ; Message length
    mov ecx, hello                 ; Message to write
    mov ebx, 1                     ; File descriptor (stdout)
    mov eax, 4                     ; System call number (sys_write)
    int 0x80                       ; Call kernel

    ; Exit
    mov eax, 1                     ; System call number (sys_exit)
    xor ebx, ebx                   ; Exit code 0
    int 0x80                       ; Call kernel
