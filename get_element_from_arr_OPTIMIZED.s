section .text

myfunction:
    enter 0, 0                  ; Enter a function!  Push rbp and move rbp to rsp

; Equivalent to "u64 pos = valuePtr + index * sizeof(T);"
    sub rsp, 8
    mov rbx, qword [rbp+16]         ; Get object reference
    mov rcx, qword [rax+8]          ; Get pointer to array
    mov ebx, dword [rbp+20]         ; Get and upcast index to pull from  (reuse eax since object no longer needed)
    lea qword [rbp-8], [rcx+rbx*4]  ; Add offset to base array pointer and store in "pos" variable

; Equivalent to "mut T result;" where sizeof(T)=4
    sub rsp, 4                      ; Make space to hold the return value

; Injected asm block for generic function
    mov rax, qword [rbp-8]          ; Load the "pos" pointer from [rbp-8] into rax

; Injected asm block built from constexpr if blocks (since sizeof(T)=4, we use rbp-5 and dword)
    mov eax, dword [rax]            ; Load value from "pos" pointer
    mov dword [rbp-12], eax         ; Store return value

; Equivalent to "return result"
    mov eax, dword [rbp-12]
    leave
    ret