section .data
    SUCCESS db 'Test Successful',10,0
    FAILURE db 'Test Failure',10,0

section .text
    global _start            ; Reference to _start for linker
_start:
    enter 0, 0

    sub rsp, 4
    mov dword [rbp-4], 100

    call myfunction

    cmp rax, 5
    jne .fail_condition

    .success_condition:
        mov rax, 0x01            ; Syscall "write"
        mov rdi, 1               ; fd for stdio
        mov rsi, SUCCESS         ; Load success string into RSI
        mov rdx, 16              ; Set string length
        syscall
        jmp .end_condition
    .fail_condition:
        mov rax, 0x01            ; Syscall "write"
        mov rdi, 1               ; fd for stdio
        mov rsi, FAILURE         ; Load fail string into RSI
        mov rdx, 13              ; Set string length
        syscall
    .end_condition:
    

    mov rax, 0x3c            ; Syscall "exit"
    xor rdi, rdi             ; Error code 0
    syscall

myfunction:
    enter 0, 0                  ; Enter a function!  Push rbp and move rbp to rsp

    mov eax, dword [rbp+16]
    cmp eax, 100

    jne .fail_condition

    .success_condition:
        mov rax, 0x01            ; Syscall "write"
        mov rdi, 1               ; fd for stdio
        mov rsi, SUCCESS         ; Load success string into RSI
        mov rdx, 16              ; Set string length
        syscall
        jmp .end_condition
    .fail_condition:
        mov rax, 0x01            ; Syscall "write"
        mov rdi, 1               ; fd for stdio
        mov rsi, FAILURE         ; Load fail string into RSI
        mov rdx, 13              ; Set string length
        syscall
    .end_condition:

    mov rax, 5
    leave
    ret