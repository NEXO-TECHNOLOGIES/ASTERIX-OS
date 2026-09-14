# ASTERIX Custom Kernel

This directory contains the custom kernel build layer for ASTERIX OS.

## Purpose

The project originally focused on the bootloader and live ISO structure. This layer adds a real custom-kernel build step so the generated ISO can bundle a custom `vmlinuz` and initramfs instead of depending only on the default Debian live kernel.

## Components

- `build-kernel.sh` — downloads a Linux source tree, applies a hardened config, builds the kernel and modules, and emits the final boot artifacts.
- `configs/asterix-kernel.config` — base architecture and security-oriented configuration for ASTERIX live builds.

## Typical workflow

From the repo root:

```bash
bash kernel/build-kernel.sh
```

This produces output under:

```text
kernel-build/out/
├── vmlinuz-asterix
├── initrd-asterix.img
├── asterix-kernel.config
└── modules/
```

## Integration with the ISO builder

The live-build script in [engine/build-iso.sh](../engine/build-iso.sh) invokes the custom kernel build automatically before `lb build` and copies the generated artifacts into the live ISO payload.

## Notes

- This is a practical starting point for an ASTERIX custom kernel, not a finished vendor-grade kernel distribution.
- The config is intentionally conservative and build-oriented, suitable for a live ISO and dual-boot environment.
- The configuration should be reviewed and tuned for additional hardware support as needed.
