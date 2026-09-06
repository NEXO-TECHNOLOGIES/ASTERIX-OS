# 🌌 ASTERIX OS v1.0 — Capa Cibernética y Entorno de Inteligencia

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 Idioma**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ ¿Qué es ASTERIX OS?

**ASTERIX OS** no es una distribución Linux convencional lenta, sino una **capa táctica de ciberseguridad, inteligencia de sistemas y operaciones de red** de alto rendimiento diseñada para ejecutarse sobre Linux (Debian, Ubuntu, Arch, Kali Linux, Parrot Security) y en entornos móviles mediante **Termux en Android**.

Está construida desde cero en cinco lenguajes nativos (**Bash, Rust, C/C++, Ensamblador NASM y Go**), unificada mediante el comando maestro `ax` / `asterix` con más de **200 comandos nativos y 15 subsistemas especializados**.

---

## 🚀 Capacidades Principales

1. **🧠 ASTERIX AI (`ax ai`)**:
   - Motor de inferencia experto sin dependencias en la nube y sin necesidad de GPU.
   - Evaluación de resiliencia del sistema (puntuación de 0 a 100) contra parámetros del kernel, ASLR, Yama ptrace, y mitigación de ataques SYN flood.
   - Diagnósticos técnicos detallados y comandos de persistencia para `/etc/sysctl.d/`.

2. **⚡ Compilador Autónomo con Auto-Reparación (`ax auto-compile`)**:
   - Compila código C, C++, Rust, Go y Ensamblador.
   - Auto-inyecta encabezados faltantes (`#include <stdio.h>`, etc.), inserta puntos y coma `;` faltantes, y resuelve banderas de enlace dinámicas (`-lpthread`, `-lssl`, `-lm`).

3. **🔧 Reparador de Código Nativo en Rust y C (`ax code-repair`)**:
   - Escaneo recursivo de proyectos de software en busca de defectos sintácticos, llaves `{}` no cerradas, paréntesis desbalanceados y finales de línea CRLF.
   - Modos: `ax code-repair scan <dir>` y `ax code-repair fix <dir>` (con copias de seguridad `.bak`).

4. **🌐 Puente de Computación y Arranque Dual (`ax os-computing`)**:
   - Detección automática de sistemas operativos vecinos o en arranque dual (Kali Linux, Parrot Security, BlackArch).
   - Asimilación de más de 80 herramientas de seguridad y diccionarios (`rockyou.txt`, `seclists`) sin duplicar espacio en disco.
   - Sinergia de aceleración por GPU (NVIDIA CUDA / AMD ROCm / OpenCL).

---

## 💻 Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. Iniciar el entorno
./setup.sh

# 3. Utilizar el comando maestro
ax help
ax ai about es
```
