# 🌌 ASTERIX OS v1.0 — Кибернетическая Среда & Система Системной Разведки

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 Язык**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ Что такое ASTERIX OS?

**ASTERIX OS** — это не медленный отдельный дистрибутив, а **высокопроизводительный тактический кибернетический слой**, созданный для наступательной и оборонительной безопасности, разведки систем и сетевых операций. Работает на любом Linux-хосте (Debian, Ubuntu, Arch, Kali Linux, Parrot), а также на смартфонах через **Termux на Android**.

Спроектирован с нуля на пяти нативных языках (**Bash, Rust, C/C++, Ассемблер NASM и Go**), управляемый через мастер-интерфейс `ax` / `asterix` с более чем **200 командами и 15 специализированными подсистемами**.

---

## 🚀 Ключевые Возможности

1. **🧠 Экспертный ИИ ASTERIX (`ax ai`)**:
   - Автономный движок логического вывода без облачных зависимостей и потребности в GPU.
   - Оценка киберустойчивости хоста (от 0 до 100) и аудит ядра (ASLR 2 уровня, ограничения памяти Yama ptrace, защита от SYN-флуда).
   - Пошаговые планы устранения уязвимостей с фиксацией в `/etc/sysctl.d/`.

2. **⚡ Автономный Самовосстанавливающийся Компилятор (`ax auto-compile`)**:
   - Сборка кода на C, C++, Rust, Go и Ассемблере.
   - Автоматическое добавление пропущенных заголовков (`#include <stdio.h>`), пропущенных точек с запятой `;` и подбор флагов компоновщика (`-lpthread`, `-lssl`, `-lm`).

3. **🔧 Нативный Движок Восстановления Кода на Rust и C (`ax code-repair`)**:
   - Рекурсивный поиск незакрытых фигурных скобок `{}`, круглых скобок, точек с запятой и нормализация переносов строк CRLF.
   - Режимы: `ax code-repair scan <dir>` и `ax code-repair fix <dir>` (с бэкапами `.bak`).

4. **🌐 Мост Dual-Boot и Вычислительной Синергии (`ax os-computing`)**:
   - Автоматическое обнаружение установленных рядом ОС (Kali Linux, Parrot, BlackArch).
   - Ассимиляция более 80 утилит безопасности и словарей (`rockyou.txt`, `seclists`) без дублирования дискового пространства.
   - Аппаратное ускорение на GPU (NVIDIA CUDA / AMD ROCm / OpenCL).

---

## 💻 Быстрый Старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. Инициализировать систему
./setup.sh

# 3. Запустить справку
ax help
ax ai about ru
```
