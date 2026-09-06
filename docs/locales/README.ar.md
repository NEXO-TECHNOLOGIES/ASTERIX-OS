# 🌌 ASTERIX OS v1.0 — بيئة الاستخبارات السيبرانية وتشغيل الأنظمة المتقدمة

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Termux%20%7C%20Dual--Boot-blueviolet.svg)](#)
[![Multi-Language Core](https://img.shields.io/badge/Core-Bash%20%7C%20Rust%20%7C%20C%2FC%2B%2B%20%7C%20Go%20%7C%20NASM-brightgreen.svg)](#)

> **🌐 اللغة**: [English](../../README.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [العربية](README.ar.md) | [Русский](README.ru.md)

---

## ⚡ ما هو نظام ASTERIX OS؟

**ASTERIX OS** ليس توزيعة لينكس تقليدية بطيئة، بل هو **طبقة تشغيلية سيبرانية تكتيكية فائقة الأداء**، مصممة لاختبار الاختراق المتقدم، واستخبارات الأنظمة، والعمليات الدفاعية على أي بيئة لينكس (Debian, Ubuntu, Arch, Kali Linux) وأيضاً على الأجهزة الذكية عبر **Termux على Android**.

تم بناؤه بالكامل بخمس لغات برمجية أصلية (**Bash و Rust و C/C++ و NASM Assembly و Go**)، ويتم التحكم به عبر واجهة الأوامر الموحدة `ax` / `asterix` بأكثر من **200 أمر و 15 نظاماً فرعياً متطوراً**.

---

## 🚀 أبرز الميزات والأنظمة الفرعية

1. **🧠 الذكاء الاصطناعي الخبير (`ax ai`)**:
   - محرك استدلال وقواعد يعمل دون اتصال بالإنترنت ودون الحاجة لمعالجات رسومية (GPU).
   - تقييم صمود النظام (من 0 إلى 100) والتحقق من إعدادات نواة لينكس (ASLR, Yama ptrace, حماية فيضانات SYN).
   - توجيهات أمنية وخطط معالجة مباشرة يتم تثبيتها في `/etc/sysctl.d/`.

2. **⚡ المترجم الذاتي الشافي (`ax auto-compile`)**:
   - يدعم لغات C و C++ و Rust و Go والتجميع (Assembly).
   - حقن الترويسات الناقصة تلقائياً (`#include <stdio.h>`)، وإصلاح الفواصل المنقوطة `;`، وربط المكتبات المطلوبة (`-lpthread`, `-lssl`, `-lm`).

3. **🔧 محرك إصلاح الشيفرات المكتوب بلغة Rust و C (`ax code-repair`)**:
   - فحص متكرر للملفات لكشف الأقواس غير المغلقة `{}`، والفواصل المنقوطة الناقصة، وإصلاح نهايات الأسطر (CRLF).
   - أوامر الفحص والإصلاح: `ax code-repair scan <dir>` و `ax code-repair fix <dir>` (مع نسخ احتياطية `.bak`).

4. **🌐 جسر الحوسبة المشتركة والإقلاع المزدوج (`ax os-computing`)**:
   - اكتشاف أنظمة الإقلاع المزدوج المجاورة تلقائياً (Kali Linux, Parrot, BlackArch).
   - ربط أكثر من 80 أداة اختراق أمنية وقوائم كلمات مرور ضخمة دون تكرار المساحة التخزينية.
   - تفعيل تسريع المعالجة عبر كروت الشاشة (NVIDIA CUDA / AMD ROCm / OpenCL).

---

## 💻 التثبيت السريع

```bash
# 1. استنساخ المستودع
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS

# 2. تشغيل الإعداد التلقائي
./setup.sh

# 3. استعراض الأوامر
ax help
ax ai about ar
```
