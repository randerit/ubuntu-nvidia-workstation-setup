# Annex C: Kernel Compatibility Matrix (Ubuntu 24.04 LTS)

> [Index](../../README_en.md#index) · [Previous: Annex B: Compatibility Verification](17-annex-b-compatibility.md) · [Español](../18-anexo-c-matriz-kernel.md)

> **What this annex is for.** The operational question is not "which version of each package am I
> running?" but "which of these components breaks if the kernel moves?". There are three. Everything
> else in the install is userspace on noble's glibc 2.39 and does not change with the kernel series.
> The snowball is not built by package versions: it is built by mixing kernel tracks.
>
> Data verified against Launchpad, the MongoDB repository and kernel.org on **21 August 2026**.

## C.1 Kernel series available for 24.04

| Series | Where it comes from | Latest published for noble | Support | MongoDB 8 |
|--------|---------------------|----------------------------|---------|-----------|
| **6.8 GA** | 24.04's own kernel | `6.8.0-138` (updates/security), `6.8.0-139` in proposed | **April 2029** standard, ESM Pro to 2034 | ✅ |
| 6.11 | HWE from 24.10 | `6.11.0-29` | Superseded series | ✅ boots |
| 6.14 | HWE from 25.04 | `6.14.0-37` | Superseded series | ✅ boots |
| 6.17 | HWE from 25.10 | `6.17.0-42` | Superseded by 7.0, goes away with the phase-out | ✅ (not validated in production) |
| 6.18 | **Ubuntu never packaged it** | — | Mainline PPA only | — |
| **7.0** | 26.04, and 24.04's current HWE | `7.0.0-30.30~24.04.1` | This is what `linux-generic-hwe-24.04` points to today | ❌ SERVER-121912 |

> **This has stopped being a future risk.** `linux-generic-hwe-24.04` in noble-updates **is already
> 7.0**. An unpinned machine running `apt full-upgrade` pulls 7.0 and loses MongoDB on the next
> reboot. The pin in [Case A of Section 14](14-runbook-mongodb8-kernel.md#case-a--machine-already-deployed-running-kernel-70) is
> the only thing stopping it.

## C.2 Is 6.18 a candidate?

It has upstream support until **December 2028** — kernel.org marks it `longterm`, released
2025-11-30 — so at first glance it looks like the elegant way out: newer than GA, older than the 6.19
that breaks MongoDB. It is not, for three reasons:

1. **Ubuntu never packaged it.** The jump was 6.17 (25.10) → 7.0 (26.04). The sources `linux-6.18`,
   `linux-hwe-6.18` and `linux-oem-6.18` do not exist in the archive, in any Ubuntu series.
2. **The only route would be the mainline PPA.** Unsigned kernels — Secure Boot has to stay off —
   with no Ubuntu patches, no security updates and no metapackage tracking them. Every kernel CVE
   becomes manual work, on every workstation.
3. **GA has more coverage, not less.** 24.04's 6.8 is supported until **April 2029**, and with ESM Pro
   until 2034: longer than 6.18's upstream December 2028, and with signed modules and headers in the
   archive so DKMS can build.

And if the reason for wanting a newer kernel is hardware — the NIC in
[Case C](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel) — the kernel is not the lever: the
answer is **a newer driver via DKMS on the old kernel**.

## C.3 The components, and which one watches the kernel

| Component | Version in use | Kernel-dependent? | Real constraint |
|-----------|----------------|-------------------|-----------------|
| **MongoDB 8.0** (`mongodb-org`, currently 8.0.28) | official repo for noble | Indirectly: its TCMalloc uses `rseq` | **Hard ceiling: breaks between 6.19 and 7.0.13** (SERVER-121912). The only component that sets an upper bound |
| **NVIDIA `.run` driver 580.x** + CUDA 13.0 + cuDNN 9 | 580 branch (upstream currently 580.178.04) | **Yes**: builds its module against the kernel headers | Moving ceiling: every new kernel can break the build until NVIDIA ships support. With a fixed kernel the problem does not exist |
| **`realtek-r8125-dkms`** (9.016.01; 9.018.00 exists since 2026-07-25) | vendor driver | **Yes** (DKMS) | Rebuilt on every kernel change. The build against a very new kernel may fail; the one that matters is the GA build |
| EMQX Enterprise 5 | EMQX repo | No (BEAM, userspace) | None |
| Node.js + Node-RED | NodeSource | No | None |
| ML stack (PyTorch and friends, via `pip`) | on noble's python3.12 | Not directly | Decided by CUDA/driver, not the kernel |
| ClamAV, Lynis, Fail2Ban, UFW, `wireguard-tools`, BorgBackup, rsync | noble | No | None |
| Snaps | noble's `snapd` | No | None |

**Three axes, not twenty.** One hard ceiling (MongoDB), one moving ceiling (NVIDIA's `.run`) and one
rebuild (DKMS). Any kernel older than 6.19 sits below MongoDB's ceiling, so a machine already
running 6.11 or 6.14 does not need to downgrade: what it needs is the pin, so it cannot move up.
Pinning GA 6.8 closes all three at once: it sits below MongoDB's ceiling, it is the
kernel this manual's 580.x was validated on, and it makes DKMS rebuilds deterministic. **As long as
the kernel does not move, there is no matrix to maintain.**

## C.4 Auditing a machine in one minute

```bash
hostname
uname -r                                             # must say 6.8.0-*
apt-cache policy linux-generic-hwe-24.04 | head -3   # with the pin, the candidate is (none)
mongod --version | head -1
nvidia-smi --query-gpu=driver_version --format=csv,noheader
dkms status
dpkg-query -W -f='${Package} ${Version} ${Status}\n' \
  'linux-image-generic*' 'r8125*' 'realtek-r8125*' 2>/dev/null
```

The doctor scripts in [Section 12](12-doctor-scripts.md#12-doctor-verification-scripts) already carry the kernel check;
this adds the version inventory to file alongside the machine.

---

> [Index](../../README_en.md#index) · [Previous: Annex B: Compatibility Verification](17-annex-b-compatibility.md) · [Español](../18-anexo-c-matriz-kernel.md)
