# 12. Doctor Verification Scripts

> [Index](../../README_en.md#index) · [Previous: 11. Post-Installation Script (Optional)](11-post-install-script.md) · [Next: 13. Security Best Practices (Optional)](13-security.md) · [Español](../12-scripts-doctor.md)

> **Note:** The doctor scripts verify that all required workstation components are installed correctly and can optionally install missing components automatically. There are three variants depending on the workstation type.

> The scripts live in [`scripts/`](../../scripts/) and the commands in this section are run from the repository root. If you copy the scripts to another machine, copy the whole `scripts/` folder: the libraries (`doctor_lib.sh`, `nic_lib.sh`) are looked up next to each script.

## Files

| File | Description |
|------|-------------|
| [`doctor_lib.sh`](../../scripts/doctor_lib.sh) | Shared library with verification, installation, and summary functions. Do not run it directly. |
| [`doctor_compresion.sh`](../../scripts/doctor_compresion.sh) | Verifies and installs components for **compression** workstations (sections 3-6). |
| [`doctor_analitica.sh`](../../scripts/doctor_analitica.sh) | Verifies and installs components for **analytics** workstations (sections 3-5 and 7). |
| [`doctor_visualizacion.sh`](../../scripts/doctor_visualizacion.sh) | Verifies and installs components for **visualization** workstations (sections 3-6, without the video stack). |
| [`self_check_doctor_lib.sh`](../../scripts/self_check_doctor_lib.sh) | Exercises `doctor_lib.sh`'s network checks against fake trees in a tmpdir. Touches nothing on the system; use it to validate library changes before shipping them to a machine. |
| [`nic_lib.sh`](../../scripts/nic_lib.sh) | Shared library holding the canonical knowledge about Realtek 2.5GbE NICs: revisions/XID, minimum driver version, `.ko` validation, and the two diagnostic rules (driver and stalled chip). Not run directly. |
| [`diag-nic.sh`](../../scripts/diag-nic.sh) | Layered diagnosis of **one** network port. Read-only plus a capture; changes no configuration. |
| [`fix-r8125-downgrade-6.8.sh`](../../scripts/fix-r8125-downgrade-6.8.sh) | Remediation: prepares the driver and the GA 6.8 kernel, verifies, and only then arms the one-shot boot. This one **does** modify the system. |
| [`self_check_nic_lib.sh`](../../scripts/self_check_nic_lib.sh) | Exercises `nic_lib.sh` and the `diag-nic.sh` rules against field scenarios A–I. No root, no hardware, no network. |

> **Since 2.3.0 the doctors verify the Case C network**, next to the kernel pin in the MongoDB
> section: that every Ethernet NIC on the PCI bus has a driver bound — the RTL8125D failure shows up
> in sysfs and needs no cable —, that every DKMS module has a build for the running kernel (an
> `r8125` built only for the previous kernel leaves the machine without network on the next reboot),
> and that nobody left a `blacklist r8169` behind, which kills RTL8168/8111 cards.


## Network diagnosis and remediation (`diag-nic.sh` and `fix-r8125-downgrade-6.8.sh`)

Both belong to [Case C of Section 14](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel) and
share `nic_lib.sh`. **Copy the whole repo to the machine**, not the individual files: without
`nic_lib.sh` next to them they refuse to start (and say so).

### Two channels, one source

These scripts — and the three doctors — also travel **inside the project's `.deb` packages**, copied
byte for byte from this repo at build time. There are not two versions to maintain: the
`Ubuntu-NVIDIA-Deb-Packages` build pulls them from here, and its suite verifies each file's sha256
against the original.

| | Loose files from this repo | Inside the `.deb` |
|---|---|---|
| What for | **Field**: fixing a conflict on an already deployed machine | **Office**: provisioning machines that go to the field |
| How they arrive | `scp` of the repo, or a USB stick | Already installed with the package |
| Invoked as | `./scripts/diag-nic.sh`, `./scripts/doctor_compresion.sh` | `nic-diag`, `workstation-doctor-compresion`, `nic-kernel-downgrade`, `workstation-doctor-analitica` |
| Where they live | Wherever you copied them | `/usr/local/lib/workstation-tools/`, with wrappers in `/usr/local/bin/` |

And the profile installer **finishes by running its doctor** (read-only, no `--fix`), so provisioning
and verifying is a single command:

```bash
sudo workstation-dependencies --perfil compresion       # first time: installs and ends with the doctor
sudo workstation-dependencies --no-doctor               # reinstall/rerun without verifying
workstation-dependencies --doctor-only                  # verify without installing
```

`--doctor-only` is the gate mode: it installs nothing, **needs no root** (the doctor in read-only
mode touches nothing) and **exits with the number of failures as its exit code**, so it can decide
whether a machine ships:

```bash
if workstation-dependencies --doctor-only; then
  echo "ready for the field"
fi
```

At the end of an install it is the other way round: there the doctor reports and does **not** change
the installer's exit code, because the install did what it could do.

> **`nic-kernel-downgrade` (that is, `fix-r8125-downgrade-6.8.sh`) is never invoked
> automatically.** The kernel pin, the NIC gate and the provisioning `grub-reboot` are already done
> by `nvidia-cuda-setup --fix-kernel` together with `nic-driver-rescue`. This script exists for
> the machine that is **already in the field** and additionally needs the ASPM/EEE hardening, the
> self-healing watchdog and the MAC-matched netplan persistence. It detects the installer's pin and
> does not write a second file, so running it afterwards is safe; what makes no sense is alternating
> between the two.

### `diag-nic.sh` — read-only

```bash
sudo ./scripts/diag-nic.sh <interface> [capture_seconds] [test_gateway]
sudo ./scripts/diag-nic.sh enp13s0 30 192.0.2.1
```

`192.0.2.1` is a documentation IP (RFC 5737): replace it with your network's gateway or a reachable server.

It leaves three artifacts in the current directory: the full log, a `.pcap` of the unfiltered
capture, and one line in `diag-results.csv` for consolidating several machines.

The summary does **not** mix observations with causes. Every finding lands in one block with one
severity:

| Block | Answers |
|---|---|
| `SALUD ACTUAL DEL LINK` | Is the NIC working right now? |
| `DRIVER / HARDWARE` | Is the bound driver the right one for this chip and this kernel? |
| `DHCP / L3` | Is there an IP and reachability? |
| `PERSISTENCIA TRAS REBOOT` | Does this survive the next reboot? |
| `RIESGOS DE CONFIGURACIÓN` | Pending good practices and switch-side hints |

| Severity | Means |
|---|---|
| `[INFO]` | Observation. Nothing to do |
| `[AVISO]` | Risk or pending good practice. **Not** a current failure |
| `[SOSPECHA]` | Consistent with a failure, but the evidence is not enough to assert it |
| `[FALLO]` | Confirmed with the available evidence |

Exit codes, for fleet consolidation: `0` no findings, `1` warnings, `2` suspicions, `3` failures.

**Two things this script deliberately does not do.** It does not flag `r8169` as the wrong driver on
its own: the rule looks at kernel, PCI ID, XID and the driver actually bound in sysfs
(`readlink -f /sys/class/net/<iface>/device/driver`, equivalent to `ethtool -i`), never `lsmod`. And
it does not declare a chip "stalled" because `rx_packets` did not move for a few seconds: it combines
RX and interrupts over a long window (>= 30 s), the unfiltered capture, and a **recent, timestamped**
`NETDEV WATCHDOG`, and reports one of four levels — `NORMAL`, `SOSPECHOSO`, `PROBABLE`,
`MUY_FUERTE`. If the capture saw traffic, the chip receives and nothing can push it past
`SOSPECHOSO`, however many signals pile up.

**Layer 8** is the one that matters before a remote downgrade: if the board has a `10ec:8125` and the
machine is not yet on GA, it verifies that an `r8125.ko` **of a sufficient version** exists for the
target 6.8 kernel and is indexed in `modules.alias`. If it is missing, the summary says
`NO REINICIAR al kernel GA todavía`.

### `fix-r8125-downgrade-6.8.sh` — modifies the system

```bash
sudo ./scripts/fix-r8125-downgrade-6.8.sh --dry-run    # see what it would do
sudo ./scripts/fix-r8125-downgrade-6.8.sh
```

It runs, in this order and on the old kernel **with the network still alive**: connectivity check,
NIC analysis and `r8125` build against the 6.8 headers, ASPM/EEE hardening, GA kernel install with
pin and hold, self-healing watchdog, MAC-matched network persistence, and only at the end a
**pre-reboot gate** that prints an auditable checklist:

```
kernel image · initramfs · configured packages (modules-extra included) ·
GRUB entry · apt pin · no r8169 blacklist ·
r8125.ko present, of sufficient version, valid for modinfo, depmod done
and PCI alias indexed
```

If anything critical is missing it prints **`NO REINICIAR`**, does not arm the one-shot boot and
exits `1`. Only with a complete checklist does it run `grub-reboot` and say `SEGURO REINICIAR`. That
ordering is deliberate: the machine is never left pointing at a kernel that cannot bring up the
network.

### Re-running is cheap: check before acting

Both scripts get re-run often — a phase fails, something is fixed, you run it again — so **no step
redoes work already done**. `fix-r8125-downgrade-6.8.sh` writes each configuration file only if its
content differs from what is already on disk, and the expensive operations hang off that:

| File | What a re-run avoids |
|---|---|
| `/etc/modprobe.d/nic-r8125-options.conf` | `update-initramfs -u -k` (~30 s) |
| `/etc/udev/rules.d/90-nic-r8125-override-*.rules` | `udevadm control --reload-rules` |
| `r8125-zombie-watchdog.sh`, `.service`, `.timer` | `systemctl daemon-reload` |
| `/etc/apt/preferences.d/99-workstation-pin-ga-kernel` | rewriting the pin |

The steps that were already guarded stay that way: it does not rebuild `r8125` if a valid one exists
for the target kernel, does not reinstall the GA kernel if the packages are properly configured, and
does not write a second pin if the installer's is already there. The watchdog's
`systemctl enable --now` does run every time, deliberately: it is idempotent and cheap, and it
repairs a timer someone disabled by hand.

`diag-nic.sh` does not apply: it only reads and captures.

> **Run `./scripts/self_check_nic_lib.sh` after touching any of those three files.** It covers field
> scenarios A–I (legitimate `r8169` on 6.8, real RTL8125D, 7.x kernel, quiet network, stalled chip
> with strong evidence, no carrier, DHCP with no Offer, ephemeral profile, undeterminable XID)
> without touching the system.

## Basic Usage

### Verify only (install nothing)
```bash
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh      # For compression workstations
./scripts/doctor_analitica.sh       # For analytics workstations
./scripts/doctor_visualizacion.sh   # For visualization workstations
```

### Verify and install missing components automatically
```bash
./scripts/doctor_compresion.sh --fix
./scripts/doctor_analitica.sh --fix
./scripts/doctor_visualizacion.sh --fix
```

With `--fix`, the script:
1. Requests `sudo` once at the start.
2. Runs `apt update` once.
3. For each failed check, attempts to install the component and verifies it again.
4. Generates a full log in `/tmp/doctor_fix_YYYYMMDD_HHMMSS.log`.

## Recommended Flow

```
1. Run the script without --fix to diagnose
             │
             ▼
2. Are there NVIDIA Driver or CUDA failures?
   ├─ YES → Install manually (sections 4 and 5 of this guide)
   └─ NO  → Continue
             │
             ▼
3. Run with --fix to install the rest automatically
             │
             ▼
4. Check the final summary
   ├─ Everything OK → Done
   └─ Still failing → Review /tmp/doctor_fix_*.log
```

> **Important:** NVIDIA drivers and CUDA Toolkit require manual installation because they involve reboots, text mode, and PATH configuration. The script detects them but does not install them automatically; instead, it shows instructions to follow the relevant sections of this guide.

## Severity Levels

The scripts classify results into different levels to make prioritization easier:

| Tag | Level | Meaning | Example | Blocks the status? |
|-----|-------|---------|---------|--------------------|
| `[OK]` | Present | Component installed and working | build-essential, nvidia-smi, MongoDB | — |
| `[FALLO]` | Necessary | The profile does not work without it | Drivers, CUDA, MongoDB, EMQX, AnyDesk override | Yes (counts for the exit code) |
| `[AVISO]` | Recommended | Works, but degraded or a real risk | Stopped services, Secure Boot, THP | Yes, for the status only |
| `[NOTA]` | Optional | Informational; no profile depends on it | Utilities, Go/VS Code, Node-RED, ML stack, RustDesk, ports not configured | No |
| `[INFO]` | Informational | Detected system data | GPU version, kernel, IP | No |

In the summary:
- **SALUDABLE:** 0 necessary and 0 recommended. Optional notes do not affect the status.
- **SALUDABLE CON AVISOS:** 0 necessary, but recommended items remain.
- **ATENCIÓN REQUERIDA:** 1-3 failures.
- **REQUIERE INTERVENCIÓN:** More than 3 failures.

## What Each Script Verifies

### Common components (both scripts)
- Operating system (Ubuntu, kernel, architecture)
- Development dependencies (build-essential, dkms, GCC, OpenGL/Mesa/GStreamer libraries)
- Quality-of-life tools (git, curl, wget, vim, htop, ncdu, nmap, etc.)
- Graphical environment (Xorg vs Wayland)
- SSH and firewall
- Development dependencies: headers for the running kernel, required for DKMS to rebuild the NVIDIA module
- NVIDIA drivers (nvidia-smi, kernel modules, GPU detection)
- Driver on the branch pinned by this manual (580.x.x) and installed via `.run`, **not** APT. A machine with `nvidia-driver-*` from APT used to pass every NVIDIA check even though [Section 4](04-nvidia-drivers.md) treats it as an error to purge
- Open/MIT-GPL kernel module, recommended by [Section 4](04-nvidia-drivers.md) Step 5 for RTX 20/30/40/50
- CUDA Toolkit (nvcc, PATH, LD_LIBRARY_PATH, system configuration)
- CUDA coherent: `nvcc`, the `/usr/local/cuda` symlink and `dpkg` all pointing at the same version. The number itself is informational — [Section 5](05-cuda-toolkit.md) pins 13.0, but a machine that arrived with 13.1 or 13.4 is valid as long as the sources agree
- Persistent GA kernel pin. Checking `uname -r` alone is not enough: a machine on 6.8 today but without the pin returns to HWE on the next `apt upgrade` and ends up with no database
- Transparent Huge Pages enabled, which MongoDB 8.0 requires

### Compression only (`doctor_compresion.sh`)
- MongoDB and MongoDB Compass, including MongoDB 8 kernel compatibility (fails if in the 6.19 – 7.0.13 range, see [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70))
- EMQX (MQTT broker)
- Golang and Visual Studio Code
- GStreamer and all plugins (base, good, bad, ugly, libav, RTSP, NVIDIA, etc.)
- Remote tools (Angry IP Scanner, AnyDesk, RustDesk)
- AnyDesk systemd override, which [Section 6](06-compression-workstations.md) Step 2 declares mandatory. Without it AnyDesk crashes and freezes GNOME, and a merely-installed package does not reveal that
- Ports: 27017 (MongoDB), 1883 (MQTT), 18083 (EMQX Dashboard)

### Analytics only (`doctor_analitica.sh`)
- MongoDB with authorization check and MongoDB 8 kernel compatibility (fails if in the 6.19 – 7.0.13 range, see [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70))
- Node-RED, Node.js, and npm
- Python 3, pip3, and ML libraries (pandas, numpy, scikit-learn, paho-mqtt, ultralytics)
- Ports: 27017 (MongoDB), 1880 (Node-RED)

### Visualization only (`doctor_visualizacion.sh`)
- Workstation that opens the web UIs and views the software; it carries dev tools in case they are needed on site
- MongoDB and MongoDB Compass (no authorization), EMQX, MQTTX, Docker, ffmpeg, AnyDesk with its X11 override, Golang and Visual Studio Code
- No GStreamer (runtime), RustDesk, Angry IP, ML stack or Node-RED
- Accepts `--skip-mongodb`, `--skip-emqx` and `--skip-snaps`: what was skipped is reported as `[INFO]`, not `[FALLO]`; the matching firewall ports are not checked (or opened with `--fix`) either: 27017 with `--skip-mongodb`, 1883 and 18083 with `--skip-emqx`
- Ports: 22 (SSH), 27017 (MongoDB), 1883 and 18083 (EMQX), AnyDesk (80, 443, 6568, 50001-50003/udp); no RTSP 554 or Node-RED 1880

## Troubleshooting
- **The script fails to start:** Verify that `doctor_lib.sh` is in the same directory.
- **"UFW not active, skipping port verification":** ufw 0.36 (Ubuntu 22.04/24.04) does not load its translations, so its output is in English today. The doctors still read it with `LANGUAGE=C LC_ALL=C` (`LANGUAGE=C LC_ALL=C sudo ufw status`), so a ufw build that does translate (`Estado: activo`) cannot break the detection, and only a `Status: active` line counts as active. `Status: inactive` skips the port checks; enable UFW ([Section 3](03-system-preparation.md)) for them to run.
- **"[AVISO] No se pudo leer el estado de UFW" (could not read the UFW status):** `ufw` is installed but `sudo ufw status` failed (your user has no sudo permission for `ufw`, or sudo asked for a password), so it is unknown whether the firewall is active and the ports go unchecked. Run `sudo ufw status` by hand to see the error. It is a warning and does not change the exit code.
- **`--fix` does not install something:** Review the log in `/tmp/doctor_fix_*.log` for the exact error.
- **Python package not detected:** The script uses `pip3 show`, which is more robust than `import`. If it fails, verify with `pip3 list | grep <package>`.
- **NVIDIA module not detected:** The script checks through `lsmod`, `/proc/driver/nvidia/version`, and `nvidia-smi` as fallback. If all fail, verify that the driver is installed correctly.
- **CUDA not detected:** The script searches for `nvcc` in `/usr/local/cuda*/bin/` and also checks configuration in `~/.bashrc`, `/etc/profile.d/`, and `/etc/environment`.
- **"Kernel compatible con MongoDB 8" fails:** There is no autofix; `--fix` cannot change the running kernel. Apply [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70) manually and re-run the script.
- **"Driver instalado por .run y no por APT" fails:** There are `nvidia-*` packages from APT. Deliberately no autofix: purging the active driver requires text mode. Apply steps 3 through 6 of [Section 4](04-nvidia-drivers.md#4-installing-nvidia-drivers-on-ubuntu).
- **"Pin del kernel GA persistente" fails:** `/etc/apt/preferences.d/99-no-hwe-kernel` or `/etc/apt/apt.conf.d/51-block-hwe-kernel` is missing, or the pin did not leave `Candidate: (none)`. Apply [Step 7 of Section 3](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version). This check can be green on `uname -r` and red here: it means the machine is fine today and broken on the next `apt upgrade`.
- **"Driver en la rama 580.x.x" fails:** The manual pins that family. Switch branches only for a concrete reason: new GPU, critical bug fixed, or internal validation. See [Annex B](17-annex-b-compatibility.md#annex-b-compatibility-verification).
- **"AnyDesk con override X11" fails:** `--fix` applies it by writing the override and restarting the service. Installing AnyDesk from scratch also applies it now.
- **An installed package reads as absent:** If it is on `hold`, `dpkg -l` shows `hi` rather than `ii`. The scripts use `pkg_installed`, which queries `dpkg-query` and is not fooled; if you write your own check, do not use `grep '^ii'`.

---

> [Index](../../README_en.md#index) · [Previous: 11. Post-Installation Script (Optional)](11-post-install-script.md) · [Next: 13. Security Best Practices (Optional)](13-security.md) · [Español](../12-scripts-doctor.md)
