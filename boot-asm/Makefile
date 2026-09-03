# =====================================================================
# ASTERIX OS - x86-64 Assembly Bootloader & Tools Makefile
# Requires: nasm, ld (binutils)
# =====================================================================

NASM   ?= nasm
LD     ?= ld
DESTDIR ?= /usr/local/bin

all: bin/asterix-mbr.bin bin/asterix-raw-info

bin/asterix-mbr.bin: asterix-mbr.asm
	@mkdir -p bin
	$(NASM) -f bin $< -o $@
	@echo "[✔] MBR sector binary: bin/asterix-mbr.bin (512 bytes)"

bin/asterix-raw-info: asterix-raw-info.asm
	@mkdir -p bin
	$(NASM) -f elf64 $< -o /tmp/asterix-raw-info.o
	$(LD) /tmp/asterix-raw-info.o -o $@
	@echo "[✔] ELF64 binary: bin/asterix-raw-info (zero libc)"

install: all
	cp bin/asterix-raw-info $(DESTDIR)/asterix-raw-info
	chmod 755 $(DESTDIR)/asterix-raw-info
	@echo "[✔] Assembly binaries installed to $(DESTDIR)"
	@echo "[!] NOTE: asterix-mbr.bin is a raw sector — write to device with:"
	@echo "    dd if=bin/asterix-mbr.bin of=/dev/sdX bs=512 count=1"

clean:
	rm -rf bin /tmp/asterix-raw-info.o
