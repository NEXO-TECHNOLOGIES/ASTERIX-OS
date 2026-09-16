# =====================================================================
# ASTERIX OS - x86-64 Assembly Bootloader & Tools Makefile
# Requires: nasm, ld (binutils)
# =====================================================================

NASM   ?= nasm
LD     ?= ld
DESTDIR ?= /usr/local/bin
NASMFLAGS ?= -f bin
LDFLAGS ?= -s -N

all: bin/asterix-mbr.bin bin/asterix-stage2-loader.bin bin/asterix-raw-info bin/asterix-cipher-asm bin/asterix-simd-crypto.o

bin/asterix-mbr.bin: asterix-mbr.asm
	@mkdir -p bin
	$(NASM) $(NASMFLAGS) $< -o $@
	@echo "[✔] MBR sector binary: bin/asterix-mbr.bin (512 bytes)"

bin/asterix-stage2-loader.bin: asterix-stage2-loader.asm
	@mkdir -p bin
	$(NASM) $(NASMFLAGS) $< -o $@
	@echo "[✔] Stage 2 loader binary: bin/asterix-stage2-loader.bin"

bin/asterix-raw-info: asterix-raw-info.asm
	@mkdir -p bin
	$(NASM) -f elf64 $< -o /tmp/asterix-raw-info.o
	$(LD) $(LDFLAGS) /tmp/asterix-raw-info.o -o $@
	@echo "[✔] ELF64 binary: bin/asterix-raw-info (zero libc)"

bin/asterix-cipher-asm: asterix-cipher-asm.asm
	@mkdir -p bin
	$(NASM) -f elf64 $< -o /tmp/asterix-cipher-asm.o
	$(LD) $(LDFLAGS) /tmp/asterix-cipher-asm.o -o $@
	@echo "[✔] ELF64 binary: bin/asterix-cipher-asm (assembly cipher engine)"

bin/asterix-simd-crypto.o: asterix-simd-crypto.asm
	@mkdir -p bin
	$(NASM) -f elf64 $< -o $@
	@echo "[✔] ELF64 SIMD Object: bin/asterix-simd-crypto.o (AVX2/SSE2 Crypto Core)"

install: all
	cp bin/asterix-raw-info $(DESTDIR)/asterix-raw-info
	cp bin/asterix-cipher-asm $(DESTDIR)/asterix-cipher-asm
	chmod 755 $(DESTDIR)/asterix-raw-info $(DESTDIR)/asterix-cipher-asm
	@echo "[✔] Assembly binaries installed to $(DESTDIR)"
	@echo "[!] NOTE: asterix-mbr.bin is a raw sector — write to device with:"
	@echo "    dd if=bin/asterix-mbr.bin of=/dev/sdX bs=512 count=1"

clean:
	rm -rf bin /tmp/asterix-raw-info.o /tmp/asterix-cipher-asm.o
