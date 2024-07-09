NASM = nasm -f elf64
LD = ld

SRC = .s
OBJ = .o

SYSCALL = syscall
TEST = testbrk

all: $(TEST)

$(TEST): $(TEST)$(OBJ) $(SYSCALL)$(OBJ)
	$(LD) $(TEST)$(OBJ) $(SYSCALL)$(OBJ) -o $(TEST)

$(TEST)$(OBJ): $(TEST)$(SRC)
	$(NASM) $(TEST)$(SRC) -o $(TEST)$(OBJ)

$(SYSCALL)$(OBJ): $(SYSCALL)$(SRC)
	$(NASM) $(SYSCALL)$(SRC) -o $(SYSCALL)$(OBJ)

clean:
	rm -f $(SYSCALL)$(OBJ) $(TEST)$(OBJ) $(TEST)
