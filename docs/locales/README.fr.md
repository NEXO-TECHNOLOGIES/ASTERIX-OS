# 🌌 ASTERIX OS v1.0 — Couche Cybernétique & Environnement d'Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 Langue**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ Qu'est-ce qu'ASTERIX OS ?

**ASTERIX OS** n'est pas une distribution Linux lente traditionnelle, mais une **couche cybernétique tactique de haute performance**, spécialisée dans la sécurité offensive et défensive, le renseignement système et les opérations réseau. Conçu pour fonctionner sur Linux (Debian, Ubuntu, Arch, Kali Linux, Parrot) ainsi que sur mobile via **Termux sous Android**.

Développé nativement en cinq langages (**Bash, Rust, C/C++, Assembleur NASM et Go**), il est piloté par la CLI unifiée `ax` / `asterix` avec plus de **200 commandes et 15 sous-systèmes spécialisés**.

---

## 🚀 Fonctionnalités Clés

1. **🧠 ASTERIX AI (`ax ai`)**:
   - Système expert SOC d'inférence fonctionnant à 100% hors-ligne (zéro dépendance cloud, zéro GPU requis).
   - Audit de cyber-résilience (0 à 100) validant les paramètres du noyau Linux (ASLR, restrictions Yama ptrace, eBPF, cookies SYN).
   - Plans d'action détaillés et commandes de persistance pour `/etc/sysctl.d/`.

2. **⚡ Compilateur Autonome Auto-Réparateur (`ax auto-compile`)**:
   - Compilation automatique pour C, C++, Rust, Go et Assembleur.
   - Injection automatique d'en-têtes manquants (`#include <stdio.h>`), correction de points-virgules `;`, et résolution dynamique des drapeaux d'édition de liens (`-lpthread`, `-lssl`, `-lm`).

3. **🔧 Moteur Natif de Réparation de Code Rust & C (`ax code-repair`)**:
   - Analyse récursive de projets pour détecter les accolades `{}` orphelines, parenthèses déséquilibrées et sauts de ligne CRLF.
   - Commandes: `ax code-repair scan <rep>` et `ax code-repair fix <rep>` (avec sauvegardes automatiques `.bak`).

4. **🌐 Pont de Calcul Multi-OS & Dual-Boot (`ax os-computing`)**:
   - Découverte automatique des partitions dual-boot (Kali Linux, Parrot Security, BlackArch).
   - Assimilation de plus de 80 outils de sécurité et dictionnaires (`rockyou.txt`, `seclists`) sans duplication d'espace disque.
   - Synergie d'accélération matérielle GPU (NVIDIA CUDA / AMD ROCm / OpenCL).

---

## 💻 Démarrage Rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. Initialiser l'environnement
./setup.sh

# 3. Utiliser la CLI
ax help
ax ai about fr
```
