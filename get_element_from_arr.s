.section .text

myfunction:
    enter 0, 0                  ; Enter a function!  Push rbp and move rbp to rsp

; Equivalent to "u64 pos = valuePtr + index * size;"
    sub rsp, 8
    mov rax, qword ptr [rbp+16]  ; Get object reference
    mov rbx, qword ptr [rbx+8]  ; Get pointer to array
    mov ecx, dword ptr [rbp+20] ; Get index to pull from
    mov dl, byte ptr [rbp-1]    ; Get size variable
    movzx edx, dl               ; Upcast u8 to u64
    mul ecx, edx                ; Multiply index by size
    movzx rcx, ecx              ; Upcast u32 to u64
    add rbx, rcx                ; Add offset to base array pointer
    mov qword ptr [rbp-8], rbx  ; Store value in "pos" variable

; Equivalent to "mut T result;" where sizeof(T)=4
    sub rsp, 4                  ; Make space to hold the return value

; Injected asm block built from constexpr if blocks (since sizeof(T)=4, we use rbp-5 and dword)
    mov dword ptr [rbp-12], dword ptr [rbx]  ; Store return value

; Equivalent to "return result"
    mov rax, dword ptr [rbp-12]
    leave
    ret