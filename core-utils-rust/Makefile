# =====================================================================
# ASTERIX OS - Native Rust Security & Systems Engines Makefile
# =====================================================================

CARGO ?= cargo
RUSTC ?= rustc
DESTDIR ?= /usr/local/bin
TARGET_DIR = target/release

ENGINES = asterix-bin-inspector \
          asterix-net-sentinel \
          asterix-crypto-core \
          asterix-sys-mon \
          asterix-guard-engine \
          asterix-dark-engine \
          asterix-log-hunter \
          asterix-defender-core

all:
	@if command -v $(CARGO) >/dev/null 2>&1; then \
		echo "[*] Compiling 7 Rust Engines via Cargo Workspace (Release)..."; \
		$(CARGO) build --release; \
	elif command -v $(RUSTC) >/dev/null 2>&1; then \
		echo "[!] Cargo not found — compiling standalone engines with rustc..."; \
		mkdir -p $(TARGET_DIR); \
		for eng in $(ENGINES); do \
			$(RUSTC) -O -C lto=yes $$eng/src/main.rs -o $(TARGET_DIR)/$$eng; \
		done; \
	else \
		echo "[!] Error: Neither cargo nor rustc found in PATH."; \
		exit 1; \
	fi

install: all
	@mkdir -p $(DESTDIR)
	@for eng in $(ENGINES); do \
		if [ -f "$(TARGET_DIR)/$$eng" ]; then \
			cp -f "$(TARGET_DIR)/$$eng" "$(DESTDIR)/"; \
			chmod 755 "$(DESTDIR)/$$eng"; \
			echo "  [✔] Installed $$eng -> $(DESTDIR)/$$eng"; \
		fi \
	done

clean:
	@if command -v $(CARGO) >/dev/null 2>&1; then \
		$(CARGO) clean; \
	else \
		rm -rf target; \
	fi