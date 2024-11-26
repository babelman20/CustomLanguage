section .data
    newline db 10            ; Save newline char as a variable
    ARG_ERROR db 'There was an arg error',10,0
    FD_ERROR db 'There was a fd error',10,0

section .bss
    buffer resb 256          ; Buffer to hold the read string (255 bytes)

section .text
    global _start            ; Reference to _start for linker

_start:
    mov rax, [rsp]
    cmp rax, 2               ; Check that there are 2 arguments
    jne arg_exit             ; If there are not 2 arguments, exit

    mov rdi, [rsp+16]        ; Store pointer to filename in RSI
    call open_file           ; Open the file

    cmp rax, 2               ; Check file descriptor (0,1,2 are reserved)
    jle fd_exit                 ; File didn't open

    push rax                 ; Save fd on the stack
    call read_line

    call write_line
    pop rax                  ; Restores fd

    call close_file

    jmp exit 

open_file:
    mov eax, 0x02             ; Syscall "open"
    mov rsi, 0                ; Open with flag RD_ONLY
    mov rdx, 0
    syscall
    ret

close_file:
    mov eax, 0x03            ; Syscall "close"
    syscall
    ret 

read_line:
    mov rcx, 0                   ; RCX holds the number of bytes read
    mov rdi, rax                 ; Move fd to RDI
    .loop:
        push rcx
        mov eax, 0               ; Syscall "read"
        lea rsi, [buffer + rcx]  ; Store next buffer position in RSI
        mov rdx, 1               ; Read 1 byte
        syscall

        cmp rax, 0               ; End if there is a null terminator
        je .done

        pop rcx
        inc rcx                  ; Increment RCX by 1
        cmp byte [rsi], 10       ; Check if char is newline
        je .done

        cmp rcx, 255             ; Check if buffer is full
        jae .done

        jmp .loop                ; Read next char

    .done:
        mov byte [buffer + rcx], 0 ; Null terminate the string
        ret

write_line:
    mov eax, 0x01            ; Syscall "write"
    mov rdi, 1               ; fd for stdio
    lea rsi, [buffer]        ; Load buffer pointer into RSI
    mov rdx, rcx             ; Get string length from buffer
    syscall

    mov rsi, 10         ; Store newline char in RSI
    mov rdx, 1               ; Write 1 char
    syscall
    ret

arg_exit:
    mov eax, 0x01            ; Syscall "write"
    mov rdi, 1               ; fd for stdio
    mov rsi, ARG_ERROR       ; Load error string into RSI
    mov rdx, 23              ; Get string length from buffer
    syscall

    jmp exit

fd_exit:
    mov eax, 0x01            ; Syscall "write"
    mov rdi, 1               ; fd for stdio
    mov rsi, FD_ERROR       ; Load error string into RSI
    mov rdx, 21              ; Get string length from buffer
    syscall

    jmp exit

exit:
    mov eax, 0x3c            ; Syscall "exit"
    xor rdi, rdi             ; Error code 0
    syscall
