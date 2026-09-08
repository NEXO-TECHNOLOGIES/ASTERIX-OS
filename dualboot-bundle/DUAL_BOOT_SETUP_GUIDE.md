# 🚀 ASTERIX OS v2.0 'Phantom' — Dual-Boot & Multi-OS Setup Guide

This bundle provides all pre-configured files to dual-boot **ASTERIX OS** alongside **Windows 10/11** or secondary operating systems from a single USB drive.

## Method 1: Rufus (Dedicated Live USB with 8 GB Persistence)
1. Download and run **Rufus** (https://rufus.ie).
2. Select your USB drive (8 GB or larger).
3. Click **SELECT** and choose `asterix-os-v2.0-amd64-full.iso` (or `stealth.iso`).
4. Move the **Persistent Partition Size** slider to `8 GB`.
5. Click **START** and select **Write in ISO Image Mode**.
6. Boot target PC (press F12 / Del / F11 at boot) and choose the USB drive.

## Method 2: Ventoy (Multi-Boot USB: ASTERIX + Windows Installer + Secondary OS)
1. Install Ventoy onto a USB flash drive (https://www.ventoy.net).
2. Copy `asterix-os-v2.0-amd64-full.iso` to the root of the Ventoy USB drive.
3. Copy the `ventoy/` folder and `persistence_asterix.dat` from this bundle into the `/ventoy/` directory on your USB.
4. Boot from the USB: Ventoy will display the ASTERIX boot menu with 8 GB persistence active.

## Dual-Boot Bootloader Menu (GRUB2):
The included `boot/grub/grub.cfg` automatically detects Windows Boot Manager on your primary SSD/NVMe drive so you can choose between Windows and ASTERIX on every boot.
