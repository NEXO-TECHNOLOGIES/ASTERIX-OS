# ASTERIX OS Downloads

This project is intentionally source-first. The verified kernel and build workflow live in the repository itself, and the recommended download path is via a standard `curl` fetch or a repository clone.

> Current project status: the kernel is verified and runnable under QEMU, but the full packaged ISO/release pipeline is still under construction.

---

## 1. Clone from GitHub

```bash
curl -L https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/archive/refs/heads/main.tar.gz -o asterix-os.tar.gz
mkdir -p asterix-os
 tar -xzf asterix-os.tar.gz -C asterix-os --strip-components=1
cd asterix-os
```

Or with git:

```bash
git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git
cd ASTERIX-OS
```

---

## 2. Clone from GitLab mirror

```bash
curl -L https://gitlab.com/nexo-technologies-group/asterix-os/-/archive/main/asterix-os-main.tar.gz -o asterix-os.gitlab.tar.gz
mkdir -p asterix-os-gitlab
 tar -xzf asterix-os.gitlab.tar.gz -C asterix-os-gitlab --strip-components=1
cd asterix-os-gitlab
```

Or with git:

```bash
git clone https://gitlab.com/nexo-technologies-group/asterix-os.git
cd asterix-os
```

---

## 3. Install and start the project

From the repository root:

```bash
chmod +x setup.sh install.sh
./setup.sh
```

If you want the one-line bootstrap flow:

```bash
curl -fsSL https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/setup.sh -o setup.sh
bash setup.sh
```

---

## 4. Kernel build path

The kernel is built directly from source, not from a downloaded prebuilt ISO image:

```bash
cd kernel
powershell -ExecutionPolicy Bypass -File .\build-kernel.ps1 --run
```

On Linux or WSL-like hosts:

```bash
cd kernel
make
```

---

## 5. Verification and integrity

After download, verify the repository is present and check the kernel build output:

```bash
ls
ls kernel/bin
```

For source integrity, prefer the standard repository itself over fake release artifacts. The project uses source-based verification and real runtime validation rather than pretending a binary ISO exists before it is actually produced.

---

## 6. Current honest status

- GitHub and GitLab mirrors are the proper public download path.
- The kernel is validated from source.
- ISO image publishing is still a pending release task.
- The recommended distribution model is source-first, not fake prebuilt distro packaging.

This keeps the project honest, reproducible, and aligned with the verified custom kernel work already in progress.
