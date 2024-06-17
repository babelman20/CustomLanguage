.section .rodata
	.globl myVar
	myVar:
		.byte 1

	.globl myVar2
	myVar2:
		.short 2

	myVar3:
		.int 3

.section .data
	.globl myVar4
	myVar4:
		.quad 4

	myVar5:
		.quad 5

	myVar6:
		.space 4