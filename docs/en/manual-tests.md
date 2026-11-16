# Manual tests

> [Index](../../README_en.md#index) · [Doctor scripts](12-doctor-scripts.md) · [Español](../pruebas-manuales.md)

This guide describes how to check, in the repository and on a real machine, that the documented steps and the scripts work. The tests go from least to most invasive: the first two do not touch the system.

## 1. Repository verification (does not touch the system)

From the repository root:

```bash
./scripts/verificar_repo.sh
```

It runs, in this order:

| Step | What it checks | Expected result |
|------|----------------|-----------------|
| `shellcheck scripts/*.sh` | Common shell mistakes in every script. Skipped if not installed (`sudo apt install shellcheck`). | No findings |
| `self_check_doctor_lib.sh` | `doctor_lib.sh` checks against fake trees in a temporary directory. | `OK: todos los self-checks pasaron` |
| `self_check_nic_lib.sh` | `nic_lib.sh` and the `diag-nic.sh` rules against field scenarios A–I. | `OK: todos los self-checks pasaron` |
| `scripts/check_links.py` | That relative links and anchors in every `.md` point to something that exists. | `0 rotos` |

Run it before copying the scripts to a machine and every time you change a library. The self-checks need no root, hardware or network.

The `shellcheck` findings that were deliberately suppressed carry a `# shellcheck disable=...` comment with the reason, right above the line.

## 2. Simulating changes (`--dry-run`)

To see what the network remediation would do without modifying anything:

```bash
sudo ./scripts/fix-r8125-downgrade-6.8.sh --dry-run
```

Expected result: the script reports each phase (connectivity, chip detection, GA 6.8 kernel) and ends without changing configuration, installing packages or scheduling a reboot: it only writes its log to `/var/log/nic-kernel-downgrade.log` and marks each action as `(dry-run)`.

## 3. Test machine: step-by-step guide

Use a machine (or a VM with GPU passthrough) that can be wiped. Each row maps to a chapter of the guide; run its verification and compare with the expected result.

| Chapter | Command | Expected result |
|---------|---------|-----------------|
| [3. Preparation](03-system-preparation.md) | `gcc --version`, `dkms status`, `ls /usr/src/linux-headers-$(uname -r)`, `echo $XDG_SESSION_TYPE` | Compiler present, headers for the running kernel, `x11` session |
| [4. NVIDIA drivers](04-nvidia-drivers.md) | `nvidia-smi` and `dkms status \| grep -i nvidia` | The GPU shows up and the module is built for the current kernel |
| [5. CUDA](05-cuda-toolkit.md) | `nvcc --version`, `readlink -f /usr/local/cuda`, `which nvcc` | The same version (13.0) in all three answers |
| [6. Compression](06-compression-workstations.md) / [7. Analytics](07-analytics-workstations.md) | `systemctl status mongod emqx` (depending on the profile) | Services `active (running)` |
| [14. MongoDB runbook](14-runbook-mongodb8-kernel.md) | `uname -r` and `apt-cache policy linux-generic-hwe-24.04` | Kernel older than 6.19 and `Candidate: (none)` if the machine is pinned to GA |

## 4. Doctor scripts on a machine

First, verify only, installing nothing:

```bash
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh     # or doctor_analitica.sh / doctor_visualizacion.sh
```

Expected result: one line per component and a summary with the four alert levels described in [chapter 12](12-doctor-scripts.md). A well-installed machine ends with no required failures.

To trigger a controlled finding and confirm the doctor catches it, stop a non-critical service (for example `sudo systemctl stop emqx`), run the doctor again and confirm it flags it; then `sudo systemctl start emqx`. To test `--fix`, run it only on the test machine:

```bash
./scripts/doctor_compresion.sh --fix
```

Expected result: it installs what is missing, verifies again and leaves the full log in `/tmp/doctor_fix_YYYYMMDD_HHMMSS.log`.

## 5. Network diagnosis

On a machine with a Realtek 2.5GbE NIC (or any interface, to see the report format):

```bash
sudo ./scripts/diag-nic.sh <interface> 20
```

Expected result: the script only reads and captures. It ends with one of these exit codes:

| Code | Meaning |
|------|---------|
| 0 | No findings above informational |
| 1 | Configuration or persistence warnings |
| 2 | Suspicions that need more evidence |
| 3 | Confirmed driver, hardware or link failure |

## 6. What to record

When done, note per machine: Ubuntu or Linux Mint version, kernel (`uname -r`), GPU and driver (`nvidia-smi --query-gpu=name,driver_version --format=csv`), the doctor profile you ran and its summary. Do not paste IP addresses, MAC addresses, hostnames or passwords into issues or commits: use example values (`192.0.2.0/24` for IPs, `00:00:5E:00:53:xx` for MACs).
