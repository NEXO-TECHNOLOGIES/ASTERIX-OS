# =====================================================================
# ASTERIX OS - Freestanding Cyber Microkernel Makefile
# Compiles x86 32-bit Multiboot Kernel with NASM and GCC
# =====================================================================

# ASTERIX kernel build
# Requires: clang, nasm, and optionally qemu-system-i386

CC      ?= clang
NASM    ?= nasm
LD      ?= ld
QEMU    ?= qemu-system-i386

CFLAGS  ?= -target i386-unknown-none-elf -ffreestanding -O2 -Wall -Wextra -fno-stack-protector -fno-builtin -fno-pie -nostdlib -mno-sse -mno-mmx -mno-sse2
ASFLAGS ?= -f elf32
LDFLAGS ?= -m elf_i386 -T linker.ld -nostdlib

SRC_DIR = src
INC_DIR = include
BIN_DIR = bin
OBJ_DIR = obj

OBJS = $(OBJ_DIR)/boot.o \
       $(OBJ_DIR)/isr.o \
       $(OBJ_DIR)/serial.o \
       $(OBJ_DIR)/paging.o \
       $(OBJ_DIR)/heap.o \
       $(OBJ_DIR)/timer.o \
       $(OBJ_DIR)/keyboard.o \
       $(OBJ_DIR)/vfs.o \
       $(OBJ_DIR)/shell.o \
       $(OBJ_DIR)/kernel.o

all: directories $(BIN_DIR)/asterix-microkernel.bin

directories:
	@mkdir -p $(BIN_DIR) $(OBJ_DIR)

$(OBJ_DIR)/boot.o: $(SRC_DIR)/boot.asm
	$(NASM) $(ASFLAGS) $< -o $@

$(OBJ_DIR)/isr.o: $(SRC_DIR)/isr.asm
	$(NASM) $(ASFLAGS) $< -o $@

$(OBJ_DIR)/serial.o: $(SRC_DIR)/serial.c $(INC_DIR)/serial.h $(INC_DIR)/kernel.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/paging.o: $(SRC_DIR)/paging.c $(INC_DIR)/paging.h $(INC_DIR)/kernel.h $(INC_DIR)/vga.h $(INC_DIR)/serial.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/heap.o: $(SRC_DIR)/heap.c $(INC_DIR)/heap.h $(INC_DIR)/serial.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/timer.o: $(SRC_DIR)/timer.c $(INC_DIR)/timer.h $(INC_DIR)/kernel.h $(INC_DIR)/serial.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/keyboard.o: $(SRC_DIR)/keyboard.c $(INC_DIR)/keyboard.h $(INC_DIR)/kernel.h $(INC_DIR)/vga.h $(INC_DIR)/serial.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/vfs.o: $(SRC_DIR)/vfs.c $(INC_DIR)/vfs.h $(INC_DIR)/serial.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/shell.o: $(SRC_DIR)/shell.c $(INC_DIR)/shell.h $(INC_DIR)/vga.h $(INC_DIR)/serial.h $(INC_DIR)/keyboard.h $(INC_DIR)/timer.h $(INC_DIR)/heap.h $(INC_DIR)/vfs.h $(INC_DIR)/kernel.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(OBJ_DIR)/kernel.o: $(SRC_DIR)/kernel.c $(INC_DIR)/kernel.h $(INC_DIR)/vga.h $(INC_DIR)/idt.h $(INC_DIR)/serial.h $(INC_DIR)/paging.h $(INC_DIR)/multiboot.h $(INC_DIR)/heap.h $(INC_DIR)/timer.h $(INC_DIR)/keyboard.h $(INC_DIR)/vfs.h $(INC_DIR)/shell.h
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

$(BIN_DIR)/asterix-microkernel.bin: $(OBJS) linker.ld
	$(CC) $(CFLAGS) -Wl,-T,linker.ld -o $(BIN_DIR)/asterix-microkernel.elf $(OBJS)
	cp $(BIN_DIR)/asterix-microkernel.elf $(BIN_DIR)/asterix-microkernel.bin
	@echo "[+] ASTERIX Microkernel built: $(BIN_DIR)/asterix-microkernel.bin"

qemu: all
	$(QEMU) -kernel $(BIN_DIR)/asterix-microkernel.bin -vga std

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)
