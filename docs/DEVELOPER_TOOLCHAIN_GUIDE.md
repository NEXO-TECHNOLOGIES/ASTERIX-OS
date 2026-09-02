# 🛠️ ASTERIX OS Developer Toolchain & Engineering Guide
### Complete Reference for Compilers, Runtimes, Reverse Engineering, and Databases

**ASTERIX OS** comes preloaded with an extensive suite of programming language compilers, package managers, debugging suites, binary analysis frameworks, database clients, and modern terminal productivity tools.

---

## 1. Programming Languages & Compilers

### 🦀 Rust Ecosystem
* **Installed Components:** `rustc`, `cargo`, `rustfmt`, `clippy`
* **Quick Compilation:** `run-rs file.rs` (Compiles and executes in one command)
* **Standard Cargo Project:**
  ```bash
  cargo new my_project --bin
  cd my_project
  cargo build --release
  cargo run
  ```

### 🐹 Go (Golang)
* **Installed Components:** `go` (Go compiler & toolchain)
* **Execution:**
  ```bash
  go run main.go
  go build -ldflags="-s -w" -o my_binary main.go
  ```

### ⚡ C / C++ & LLVM Toolchain
* **Installed Compilers:** `gcc`, `g++`, `clang`, `llvm`, `make`, `cmake`, `ninja-build`
* **Debuggers & Profilers:** `gdb`, `valgrind`, `strace`, `ltrace`
* **Quick Compilation:** `run-c file.c`
* **Compilation with GCC/Clang:**
  ```bash
  gcc -O2 -Wall file.c -o file && ./file
  g++ -std=c++20 -O2 file.cpp -o file && ./file
  ```

### 🐍 Python 3 & Virtual Environments
* **Installed Components:** `python3`, `python3-pip`, `python3-venv`, `python3-dev`, `ipython3`, `pipx`
* **Interactive REPL:** `ipython3`
* **Virtual Environment Setup:**
  ```bash
  python3 -m venv ~/asterix_persistent/my_venv
  source ~/asterix_persistent/my_venv/bin/activate
  pip install --upgrade pip
  ```

### 🌐 Node.js & Web Runtimes
* **Installed Components:** `nodejs`, `npm`
* **Run Script:** `node script.js`
* **Package Management:** `npm init -y && npm install <package>`

---

## 2. Binary Analysis & Reverse Engineering Suite

| Tool | Command | Description |
| :--- | :--- | :--- |
| **Radare2 / R2** | `r2 -AA <binary>` | Comprehensive binary disassembly, debugging, and analysis framework |
| **Binwalk** | `binwalk -e <firmware.bin>` | Firmware extraction and file signature scanner |
| **Hexedit** | `hexedit <file>` | In-terminal interactive raw hexadecimal editor |
| **XXD** | `xxd <binary> \| head -n 30` | Hex dump generator and patch applicator |
| **GDB** | `gdb <binary>` | GNU Debugger with breakpoint and register inspection |
| **Strace / Ltrace** | `strace -f <cmd>` | System call and dynamic library tracer |

---

## 3. Databases & API Testing Suite

### 🗄️ Database Consoles
* **SQLite3 (Local Relational):**
  ```bash
  sqlite3 /asterix_persistent/database.db
  ```
* **PostgreSQL Client:** `psql -h <host> -U <user> -d <dbname>`
* **Redis CLI:** `redis-cli -h <host>`

### 📡 API & HTTP Testing (HTTPie & Socat)
* **HTTPie JSON API Request:**
  ```bash
  http GET https://httpbin.org/json
  http POST https://httpbin.org/post user=asterix role=root
  ```
* **Socat Encrypted Relays:**
  ```bash
  socat TCP-LISTEN:8080,fork TCP:127.0.0.1:80
  ```

---

## 4. Modern CLI Power Utilities

| Utility | Command Example | Feature |
| :--- | :--- | :--- |
| **Ripgrep (`rg`)** | `rg "fn main" src/` | Ultra-fast recursive search (replaces standard grep) |
| **Fd-Find (`fd`)** | `fd -e rs` | Fast, user-friendly file finder (replaces find) |
| **Bat (`batcat`)** | `batcat code.rs` | Cat clone with syntax highlighting and git integration |
| **FZF** | `fzf` | Interactive terminal fuzzy finder |
| **Zoxide (`z`)** | `z projects` | Smart directory jumper that learns your habits |
| **LazyGit** | `lazygit` | Interactive terminal UI for Git branches and commits |
| **JQ / YQ** | `curl ... \| jq '.data'` | Streamlined command-line JSON and YAML processor |
| **TLDR** | `tldr tar` | Practical, community-driven man page summaries |
| **NCDU** | `ncdu /` | Interactive ncurses disk space analyzer |

---

## 5. Developer Workspace Persistence

To ensure all your cloned repositories, Python virtual environments, compiled binaries, and database files remain intact across live USB reboots and Termux updates:

1. Always store your developer projects in:
   `/asterix_persistent/projects/`
2. On Android Termux, this directory automatically syncs with:
   `/sdcard/ASTERIX_PERSISTENCE/projects/`
