# =====================================================================
# ASTERIX OS - System Tracer Makefile
# =====================================================================

CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -D_GNU_SOURCE
DESTDIR ?= /usr/local/bin

all: bin/proc_tracer

bin/proc_tracer: src/proc_tracer.c
	@mkdir -p bin
	$(CC) $(CFLAGS) $< -o $@

install: all
	cp bin/proc_tracer $(DESTDIR)/asterix-proctrace
	chmod 755 $(DESTDIR)/asterix-proctrace
	@echo "[✔] Installed asterix-proctrace to $(DESTDIR)/"

clean:
	rm -rf bin
