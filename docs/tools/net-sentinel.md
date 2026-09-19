# [*] `net-sentinel` — High-Throughput Network Engine

A compiled Rust network scanner and packet auditor optimized for ultra-low memory overhead and multi-threaded port discovery.

---

##  Usage

```bash
ax sentinel scan <host> [--ports 1-1024] [--threads 128]
ax sentinel sniff <interface> [--pcap output.pcap]
```

---

## [*] Key Capabilities

- **Zero-Copy I/O**: Implemented in Rust with memory-mapped buffers for packet processing.
- **High Concurrency**: Asynchronous TCP socket probing capable of scanning 1,000 ports in under 12 seconds with <12 MB RAM usage.
- **Mobile Friendly**: Designed to run inside resource-constrained environments (ARM64 Android Termux PRoot and AVF VMs).
