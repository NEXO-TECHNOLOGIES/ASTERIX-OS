# 🌌 ASTERIX OS v1.0 — 网络作战层与系统情报环境

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 语言**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ 什么是 ASTERIX OS？

**ASTERIX OS** 并非传统的单一 Linux 发行版，而是一个专为专业渗透测试、系统情报与攻防作战打造的**高性能战术网络作战框架层**。它可原生运行于任何 Linux 主机（Debian、Ubuntu、Arch、Kali Linux、Parrot）以及通过 **Android Termux** 运行于移动端。

底层使用五种原生编程语言构建（**Bash、Rust、C/C++、NASM 汇编与 Go**），通过主控制命令 `ax` / `asterix` 提供 **200+ 原生命令与 15 个作战子系统**。

---

## 🚀 核心架构与功能

1. **🧠 ASTERIX 专家级 AI (`ax ai`)**:
   - 纯离线规则推理引擎，零云端依赖、零 GPU 算力要求。
   - 自动化系统弹性评分（0-100分），全方位审计 Linux 内核参数（ASLR 2级随机化、Yama 内存注入防护、SYN 泛洪防护）。
   - 详细的威胁分析模型与针对 `/etc/sysctl.d/` 的持久化防御配置指令。

2. **⚡ 自主代码自愈编译器 (`ax auto-compile`)**:
   - 支持 C、C++、Rust、Go、NASM 源码与项目目录（Makefile、Cargo.toml）。
   - 遇到编译错误时自动注入缺失头文件（`#include <stdio.h>` 等）、修复缺失分号 `;`，并自动解析链接库标记（`-lpthread`、`-lssl`、`-lm`）。

3. **🔧 原生 Rust 与 C 代码修复引擎 (`ax code-repair`)**:
   - 极速遍历项目源码，自动修复未闭合的花括号 `{}`、圆括号、缺失分号与 CRLF 换行符。
   - 命令：`ax code-repair scan <路径>` 与 `ax code-repair fix <路径>`（自动备份为 `.bak`）。

4. **🌐 双系统协同与算力桥接 (`ax os-computing`)**:
   - 自动探测同机挂载的双系统分区（Kali Linux、Parrot、BlackArch）。
   - 一键将 80+ 款安全工具与海量密码字典（`rockyou.txt`、`seclists`）软链接聚合至 ASTERIX 环境，不额外占用磁盘。
   - 自动激活 GPU 硬件算力协同（NVIDIA CUDA / AMD ROCm / OpenCL）。

---

## 💻 快速安装

```bash
# 1. 克隆代码仓库
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. 一键初始化环境
./setup.sh

# 3. 查看中文指令总览
ax help
ax ai about zh
```
