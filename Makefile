NASM = nasm -f elf64
LD = ld

BUILDPATH = CustomLang/build/intermediaries/
OUTPUTPATH = CustomLang/build/output/

SRC = .s
OBJ = .o

ARRAY = customlang.utils.array
SYSCALL = customlang.utils.Syscall
TEST = testfile

all: $(OUTPUTPATH)$(TEST) $(OUTPUTPATH)$(ARRAY)

$(OUTPUTPATH)$(TEST): $(BUILDPATH)$(TEST)$(OBJ) $(BUILDPATH)$(SYSCALL)$(OBJ)
	$(LD) $(BUILDPATH)$(TEST)$(OBJ) $(BUILDPATH)$(SYSCALL)$(OBJ) -o $(OUTPUTPATH)$(TEST)

$(BUILDPATH)$(TEST)$(OBJ): $(BUILDPATH)$(TEST)$(SRC)
	$(NASM) $(BUILDPATH)$(TEST)$(SRC) -o $(BUILDPATH)$(TEST)$(OBJ)

$(OUTPUTPATH)$(ARRAY): $(BUILDPATH)$(ARRAY)$(OBJ)
	$(LD) $(BUILDPATH)$(ARRAY)$(OBJ) -o $(OUTPUTPATH)$(ARRAY)

$(BUILDPATH)$(ARRAY)$(OBJ): $(BUILDPATH)$(ARRAY)$(SRC)
	$(NASM) $(BUILDPATH)$(ARRAY)$(SRC) -o $(BUILDPATH)$(ARRAY)$(OBJ)

$(BUILDPATH)$(SYSCALL)$(OBJ): $(BUILDPATH)$(SYSCALL)$(SRC)
	$(NASM) $(BUILDPATH)$(SYSCALL)$(SRC) -o $(BUILDPATH)$(SYSCALL)$(OBJ)

clean:
	rm -f $(BUILDPATH)$(SYSCALL)$(OBJ) $(BUILDPATH)$(TEST)$(OBJ) $(OUTPUTPATH)$(TEST) $(BUILDPATH)$(ARRAY)$(OBJ) $(OUTPUTPATH)$(ARRAY)
