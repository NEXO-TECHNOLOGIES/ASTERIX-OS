# =====================================================================
# 🌌 ASTERIX OS — Freestanding Cyber Microkernel Makefile
# Compiles x86 32-bit Multiboot Kernel with NASM and GCC
# =====================================================================

CC      ?= gcc
NASM    ?= nasm
LD      ?= ld
QEMU    ?= qemu-system-i386

CFLAGS  ?= -m32 -ffreestanding -O2 -Wall -Wextra -nostdlib -fno-builtin -fno-stack-protector
ASFLAGS ?= -f elf32
LDFLAGS ?= -m elf_i386 -T linker.ld -nostdlib

SRC_DIR = src
INC_DIR = include
BIN_DIR = bin
OBJ_DIR = obj

OBJS = $(OBJ_DIR)/boot.o \
       $(OBJ_DIR)/isr.o \
       $(OBJ_DIR)/kernel.o

all: directories $(BIN_DIR)/asterix-microkernel.bin

directories:
	@mkdir -p $(BIN_DIR) $(OBJ_DIR)

$(OBJ_DIR)/boot.o: $(SRC_DIR)/boot.asm
	$(NASM) $(ASFLAGS) $< -o $@

$(OBJ_DIR)/isr.o: $(SRC_DIR)/isr.asm
	$(NASM) $(ASFLAGS) $< -o $@

$(OBJ_DIR)/kernel.o: $(SRC_DIR)/kernel.c $(INC_DIR)/kernel.h $(INC_DIR)/vga.h $(INC_DIR)/idt.h
	$(CC) $(CFLAGS) -c $< -o $@

$(BIN_DIR)/asterix-microkernel.bin: $(OBJS) linker.ld
	$(LD) $(LDFLAGS) $(OBJS) -o $@
	@echo "[✔] ASTERIX Microkernel built: $(BIN_DIR)/asterix-microkernel.bin"

qemu: all
	$(QEMU) -kernel $(BIN_DIR)/asterix-microkernel.bin -vga std

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)
