#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - One-Click Multi-Language Developer Workspace Scaffolder
# Generates Rust, C/C++, Go, Python, and Node.js project skeletons
# =====================================================================

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

print_banner() {
    echo -e "${C_CYAN}${C_BOLD}"
    cat << 'EOF'
    ___   _____ ______ ______ ____     ____  _______    __
   /   | / ___//_  __// ____// __ \   / __ \/ ____/ |  / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / __/  | | / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /___  | |/ /  
/_/  |_/____/ /_/  /_____//_/ |_|  /_____/_____/  |___/   
       DEVELOPER WORKSPACE SCAFFOLDING ENGINE
EOF
    echo -e "${C_RESET}"
}

scaffold_rust() {
    local name="$1"
    mkdir -p "${name}/src"
    cat > "${name}/Cargo.toml" << EOF
[package]
name = "${name}"
version = "0.1.0"
edition = "2021"

[dependencies]
EOF
    cat > "${name}/src/main.rs" << 'EOF'
fn main() {
    println!("Hello from ASTERIX OS Rust workspace!");
}
EOF
    echo -e "${C_GREEN}[✔] Rust project '${name}' scaffolded!${C_RESET}"
    echo -e "  Run: ${C_YELLOW}cd ${name} && cargo build --release${C_RESET}"
}

scaffold_c() {
    local name="$1"
    mkdir -p "${name}/src"
    cat > "${name}/src/main.c" << 'EOF'
#include <stdio.h>
int main() {
    printf("Hello from ASTERIX OS C workspace!\n");
    return 0;
}
EOF
    cat > "${name}/Makefile" << EOF
CC=gcc
CFLAGS=-O2 -Wall -Wextra
all:
	\$(CC) \$(CFLAGS) src/main.c -o ${name}
clean:
	rm -f ${name}
EOF
    echo -e "${C_GREEN}[✔] C project '${name}' scaffolded!${C_RESET}"
    echo -e "  Run: ${C_YELLOW}cd ${name} && make${C_RESET}"
}

scaffold_go() {
    local name="$1"
    mkdir -p "${name}"
    cat > "${name}/main.go" << EOF
package main

import "fmt"

func main() {
    fmt.Println("Hello from ASTERIX OS Go workspace!")
}
EOF
    cat > "${name}/go.mod" << EOF
module ${name}

go 1.21
EOF
    echo -e "${C_GREEN}[✔] Go project '${name}' scaffolded!${C_RESET}"
    echo -e "  Run: ${C_YELLOW}cd ${name} && go build && ./${name}${C_RESET}"
}

scaffold_python() {
    local name="$1"
    mkdir -p "${name}"
    cat > "${name}/main.py" << 'EOF'
#!/usr/bin/env python3

def main():
    print("Hello from ASTERIX OS Python workspace!")

if __name__ == "__main__":
    main()
EOF
    cat > "${name}/requirements.txt" << 'EOF'
# Add your Python dependencies here
EOF
    chmod +x "${name}/main.py"
    echo -e "${C_GREEN}[✔] Python project '${name}' scaffolded!${C_RESET}"
    echo -e "  Run: ${C_YELLOW}cd ${name} && python3 main.py${C_RESET}"
}

scaffold_node() {
    local name="$1"
    mkdir -p "${name}/src"
    cat > "${name}/src/index.js" << 'EOF'
'use strict';

function main() {
    console.log("Hello from ASTERIX OS Node.js workspace!");
}

main();
EOF
    cat > "${name}/package.json" << EOF
{
  "name": "${name}",
  "version": "1.0.0",
  "description": "ASTERIX OS Node.js Project",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js"
  }
}
EOF
    echo -e "${C_GREEN}[✔] Node.js project '${name}' scaffolded!${C_RESET}"
    echo -e "  Run: ${C_YELLOW}cd ${name} && node src/index.js${C_RESET}"
}

print_banner

LANG="${1}"
PROJECT_NAME="${2:-asterix-project}"

if [ -z "$LANG" ]; then
    echo -e "${C_YELLOW}Available Languages:${C_RESET}"
    echo "  1) rust      - Cargo workspace with src/main.rs"
    echo "  2) c         - GCC Makefile workspace with src/main.c"
    echo "  3) go        - Go module workspace"
    echo "  4) python    - Python3 workspace with requirements.txt"
    echo "  5) node      - Node.js workspace with package.json"
    echo ""
    echo -e "Usage: ${C_CYAN}dev-bootstrap.sh <lang> <project_name>${C_RESET}"
    exit 0
fi

case "$LANG" in
    rust)    scaffold_rust "$PROJECT_NAME" ;;
    c|cpp)   scaffold_c "$PROJECT_NAME" ;;
    go)      scaffold_go "$PROJECT_NAME" ;;
    python)  scaffold_python "$PROJECT_NAME" ;;
    node|js) scaffold_node "$PROJECT_NAME" ;;
    *)
        echo -e "${C_RED}[!] Unknown language: ${LANG}${C_RESET}"
        echo "Supported: rust, c, go, python, node"
        exit 1
        ;;
esac
