# 🌌 ASTERIX OS v1.0 — Cybernetische Ebene & System-Intelligenzumgebung

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 Sprache**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ Was ist ASTERIX OS?

**ASTERIX OS** ist keine gewöhnliche Linux-Distribution, sondern eine **leistungsstarke taktische Cybersicherheitsschicht**, die auf jedem Linux-Host (Debian, Ubuntu, Arch, Kali Linux, Parrot) und mobil unter **Termux auf Android** ausgeführt werden kann.

Nativ entwickelt in fünf Programmiersprachen (**Bash, Rust, C/C++, Assembler NASM und Go**), vereint unter der Master-CLI `ax` / `asterix` mit mehr als **200 nativen Befehlen und 15 Teilsystemen**.

---

## 🚀 Hauptfunktionen

1. **🧠 ASTERIX AI (`ax ai`)**:
   - Regelbasiertes SOC-Expertensystem ohne Cloud-Abhängigkeiten oder GPU-Bedarf.
   - Cyber-Resilienz-Bewertung (0 bis 100 Punkte) zur Verifikation von Kernel-Parametern (ASLR Stufe 2, Yama ptrace, SYN-Cookies).
   - Detaillierte Maßnahmenpläne und Persistenzbefehle für `/etc/sysctl.d/`.

2. **⚡ Autonomer Selbstheilender Compiler (`ax auto-compile`)**:
   - Automatische Erkennung und Kompilierung von C, C++, Rust, Go und Assembler.
   - Automatische Injektion fehlender Header (`#include <stdio.h>`), Semicolon-Reparatur `;` und Linker-Flag-Auflösung (`-lpthread`, `-lssl`, `-lm`).

3. **🔧 Nativer Code-Reparatur-Engine in Rust & C (`ax code-repair`)**:
   - Rekursives Scannen von Projekten nach Syntaxfehlern, ungeschlossenen Klammern `{}` und Windows-CRLF-Zeilenumbrüchen.
   - Modi: `ax code-repair scan <dir>` und `ax code-repair fix <dir>` (inkl. automatischer `.bak`-Sicherungen).

4. **🌐 Dual-Boot- & Host-Kollaborationsbrücke (`ax os-computing`)**:
   - Automatische Erkennung parallel installierter Dual-Boot-Systeme (Kali Linux, Parrot, BlackArch).
   - Verknüpfung von über 80 Sicherheitswerkzeugen und Wortlisten (`rockyou.txt`, `seclists`) ohne Festplattenspeicher-Duplizierung.
   - GPU-Rechenbeschleunigung (NVIDIA CUDA / AMD ROCm / OpenCL).

---

## 💻 Schnellstart

```bash
# 1. Repository klonen
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. Umgebung starten
./setup.sh

# 3. Master-Befehl ausführen
ax help
ax ai about de
```
