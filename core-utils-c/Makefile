# =====================================================================
# ASTERIX OS - Native C Systems Utilities Makefile
# =====================================================================

CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -D_GNU_SOURCE
LDFLAGS ?= 
DESTDIR ?= /usr/local/bin

SRCS = src/asterix-sysinfo.c \
       src/asterix-memview.c \
       src/asterix-netprobe.c \
       src/asterix-hasher.c \
       src/asterix-shredder.c

BINS = bin/asterix-sysinfo \
       bin/asterix-memview \
       bin/asterix-netprobe \
       bin/asterix-hasher \
       bin/asterix-shredder

all: directories $(BINS)

directories:
	@mkdir -p bin

bin/asterix-sysinfo: src/asterix-sysinfo.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

bin/asterix-memview: src/asterix-memview.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

bin/asterix-netprobe: src/asterix-netprobe.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

bin/asterix-hasher: src/asterix-hasher.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

bin/asterix-shredder: src/asterix-shredder.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

install: all
	@mkdir -p $(DESTDIR)
	@cp -f bin/* $(DESTDIR)/
	@chmod 755 $(DESTDIR)/asterix-*
	@echo "[✔] Installed all ASTERIX native C binaries to $(DESTDIR)/"

clean:
	@rm -rf bin
