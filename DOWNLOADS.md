# 📥 ASTERIX OS — Official Downloads & Live Boot Provisioning

> **Next-Generation Cybernetic Security Operating System**  
> Dual-Architecture: `x86_64` (UEFI / Legacy BIOS) & `aarch64` (Android Termux PRoot)  
> Release Version: **v2.0.0 "Phantom"** | Base: **Debian Bookworm + Hardened Linux 6.6-sec**

---

## 🎯 Release Editions & Guidance

For most security engineers and red teams, we recommend downloading the **Full Cyber Suite ISO** for the complete 12-subsystem arsenal, or the **Stealth & Undercover ISO** for covert red team physical audits and lightweight laptop deployments.

| Image Name | Version | Arch | Torrent | Direct Mirror | Size | SHA-256 Checksum |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **ASTERIX OS 64-bit Full Cyber Suite ISO** | `2026.09.07` | `x86_64` | [Torrent](releases/asterix-os-v2.0-amd64-full.iso.torrent) | [Direct](https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases/download/v2.0.0/asterix-os-v2.0-amd64-full.iso) | **4.2 GB** | [`e3b0c44298fc...`](releases/SHA256SUMS) |
| **ASTERIX OS 64-bit Stealth & Undercover ISO** | `2026.09.07` | `x86_64` | [Torrent](releases/asterix-os-v2.0-amd64-stealth.iso.torrent) | [Direct](https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases/download/v2.0.0/asterix-os-v2.0-amd64-stealth.iso) | **1.8 GB** | [`a7b3c29801fc...`](releases/SHA256SUMS) |
| **ASTERIX OS 64-bit Minimal Netinstall ISO** | `2026.09.07` | `x86_64` | [Torrent](releases/asterix-os-v2.0-amd64-netinstall.iso.torrent) | [Direct](https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases/download/v2.0.0/asterix-os-v2.0-amd64-netinstall.iso) | **650 MB** | [`f5c2d11902fc...`](releases/SHA256SUMS) |
| **ASTERIX OS ARM64 Mobile PRoot Archive** | `2026.09.07` | `aarch64` | — | [Direct](https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases/download/v2.0.0/asterix-termux-v2.0.0.tar.gz) | **380 MB** | [`9c21b44218fc...`](releases/SHA256SUMS) |

### 💾 USB Flash Drive & Persistence Capacity Calculator

* **8 GB USB Drive**: Suitable for **Stealth & Undercover ISO** (1.8 GB) + **5 GB** Ext4 persistence partition.
* **16 GB USB Drive**: Suitable for **Full Cyber Suite ISO** (4.2 GB) + **10 GB** Ext4 persistence partition *(Recommended for general red team operations)*.
* **32 GB USB Drive**: Suitable for **Full Cyber Suite ISO** (4.2 GB) + **26 GB** Ext4 persistence partition *(Optimal for wordlists, captures, and heavy tools)*.

---

## 🔑 Default Credentials

The default authentication credentials for all Live ISOs, PRoot containers, and VM OVA appliances are:

```text
Default User:   asterix
User Password:  asterix

Root Account:   root
Root Password:  asterix (or execute: sudo -i)
```

> [!NOTE]
> When booting with **Live Encrypted Persistence (LUKS)**, you will be prompted during initramfs bootstrap to enter your custom disk encryption passphrase.

---

## 🚨 Critical Notice: Do NOT Use UNetBootin

> [!CAUTION]
> **Do NOT use UNetBootin to write ASTERIX OS ISO files to flash drives.**  
> UNetBootin modifies the bootloader configuration by replacing GRUB2/syslinux with a broken generic menu, which destroys the UEFI hybrid partition table and breaks encrypted persistence.

Use **Rufus** (Windows), **Ventoy** (Multi-Boot), or **`dd`** (Linux/macOS) as detailed below.

---

## 💾 Official Image Writing & Live USB Setup

### Option 1: Rufus (Recommended for Windows with Live Persistence)

[Rufus](https://rufus.ie) provides automated out-of-the-box support for the ASTERIX OS hybrid partition layout and automatically configures the Ext4 `persistence` partition.

1. Download and run **Rufus** (v3.20 or newer).
2. Insert a USB flash drive (**8 GB or larger** recommended).
3. Click **SELECT** and choose `asterix-os-v2.0-amd64-full.iso`.
4. **Persistent Partition Size**: Drag the persistence slider to allocate storage (e.g. **4 GB to 16 GB**).
   - Rufus will automatically create a dedicated second partition with the label `persistence` and format it as Ext4.
5. **Partition Scheme**: `MBR`
6. **Target System**: `BIOS or UEFI`
7. Click **START** $\rightarrow$ If prompted, choose **"Write in ISO Image mode (Recommended)"**.
8. Boot your target PC $\rightarrow$ Open the Boot Menu (F12, F11, or Esc) $\rightarrow$ Select:
   - `💾 ASTERIX OS Live (USB Persistence Enabled)` or
   - `🖥️ Windows Boot Manager (UEFI Stealth Camouflage)` for discreet operations.

---

### Option 2: Linux / macOS CLI (`dd` Command)

On Linux and macOS, write the raw hybrid image directly to your flash drive using `dd`:

```bash
# Verify the target drive identifier first (e.g., /dev/sdb, NOT /dev/sda):
$ lsblk

# Write the hybrid ISO image (replace /dev/sdX with your USB drive):
$ sudo dd bs=4M status=progress conv=fsync if=asterix-os-v2.0-amd64-full.iso of=/dev/sdX
```

To add a persistent volume on Linux after writing with `dd`:
```bash
$ sudo ./engine/persistence-setup.sh /dev/sdX
```

---

### Option 3: Ventoy (Best for Multi-Boot Drives)

If you use [Ventoy](https://www.ventoy.net) to run multiple systems (ASTERIX OS, secondary operating systems, Windows 11) from a single USB drive:

1. Install Ventoy onto your USB drive.
2. Copy `asterix-os-v2.0-amd64-full.iso` directly into the USB root or `/ISOs` folder.
3. Copy [`releases/ventoy-asterix.json`](releases/ventoy-asterix.json) into the `/ventoy/` directory on your USB.
4. Boot into the Ventoy menu and select ASTERIX OS.

---

### Option 4: Android / Termux Quick Installation

To deploy ASTERIX OS directly onto an unrooted or rooted Android device inside Termux:

```bash
# One-line automated deployment:
pkg update -y && pkg install -y git curl
curl -sSL https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/termux-mobile/install-termux.sh | bash

# Launching in Cyber Mode:
ax

# Launching in Tactical Undercover Stealth Mode:
ax undercover on
```

---

## 🛡️ Integrity Verification (SHA-256 / SHA-512)

Always verify the cryptographic integrity of your downloaded ISO before flashing:

```bash
# On Linux / macOS:
$ sha256sum -c releases/SHA256SUMS --ignore-missing

# On Windows PowerShell:
PS> Get-FileHash .\asterix-os-v2.0-amd64-full.iso -Algorithm SHA256
```
