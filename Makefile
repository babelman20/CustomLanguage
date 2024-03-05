NASM = nasm -f elf64
LD = ld -o
G++ = g++ -g -o

COMPILER_SRC = compiler.cpp
COMPILER = compiler

TEST_SRC = testfile.s
TEST_OBJ = testfile.o
TEST_EXE = testfile

all: $(TEST_EXE) $(COMPILER)

$(COMPILER): $(COMPILER_SRC)
	$(G++) $(COMPILER) $(COMPILER_SRC)

$(TEST_EXE): $(TEST_OBJ)
	$(LD) $(TEST_EXE) $(TEST_OBJ)

$(TEST_OBJ): $(TEST_SRC)
	$(NASM) $(TEST_SRC)

clean:
	rm -f $(TEST_OBJ) $(TEST_EXE) $(COMPILER)
