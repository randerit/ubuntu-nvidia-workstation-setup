# 14. Runbook: MongoDB 8 Fails to Start on HWE Kernel 7.0

> [Index](../../README_en.md#index) · [Previous: 13. Security Best Practices (Optional)](13-security.md) · [Next: FAQ: Frequently Asked Questions](15-faq.md) · [Español](../14-runbook-mongodb8-kernel.md)

> **Applies to:** Ubuntu 24.04 LTS (noble) with `mongodb-org` 8.0.x.
> **Upstream ticket:** [SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912).
> **Status:** mitigation in force until MongoDB ships the patched TCMalloc (see *Exit criteria*).
> **Validated on:** `test-workstation`, August 3, 2026.

This section is a runbook: apply it only when the symptom shows up (Case A) or when provisioning a
new machine (Case B). It is not part of the normal installation flow.

## Root Cause

MongoDB 8.0+ vendors a version of TCMalloc that violates the kernel's **rseq**
(*restartable sequences*) ABI. From Linux 6.19 onward this causes crashes.

MongoDB added an explicit guard: **it detects kernels in the 6.19 – 7.0.13 range and refuses to
start**. Kernel 7.0.14 or newer resolves the incompatibility.

The problem shows up on Ubuntu 24.04 because Canonical rolled the **26.04 HWE stack (kernel 7.0)**
into noble. ISOs from 24.04.4 onward install it by default on desktop.

### Critical detail for Ubuntu

Ubuntu keeps `X.Y.0-ABI` fixed in `uname -r` and only bumps the ABI number, even when it rebases the
upstream sublevel internally. That means: **when Canonical rebases to 7.0.14+, `uname -r` will still
report `7.0.0-XX`** and MongoDB's guard will keep blocking, even on an already-fixed kernel.

**Operational conclusion:** do not wait for the next HWE update to fix it. The way out is staying on
the **GA 6.8** track, which receives Canonical security patches until 24.04 end of life and never
jumps branches.

## Diagnosis

```bash
uname -r                        # e.g. 7.0.0-28-generic
cat /proc/version_signature     # REAL upstream base, e.g. "... 7.0.12"
systemctl status mongod
journalctl -u mongod -b --no-pager | tail -30
```

Unmistakable signature in the journal:

```
"s":"F","c":"CONTROL","id":12257600,"ctx":"main",
"msg":"MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility..."
```

`/proc/version_signature` tells the two cases apart:

| Upstream base | Situation |
|---|---|
| ≤ 6.18 | Compatible: `mongod` starts. Do not apply this runbook; the pin from [Step 7](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version) is enough. |
| 6.19 – 7.0.13 | Real incompatibility. Apply this runbook. |
| ≥ 7.0.14 | Kernel already fixed, but the guard blocks because of the `uname` string. Apply this runbook anyway. |

## Case A — Machine Already Deployed Running Kernel 7.0

> **Mandatory order:** pinning → purge → verify GRUB → reboot.
> Reversing it leaves windows where apt reinstalls HWE, or where the machine boots into 7.0 unattended.

> **With the `.deb` packages 2.4.0+ this runbook is automated**, in that same order:
>
> ```bash
> sudo nvidia-cuda-setup --fix-kernel   # pin + NIC gate + one-shot boot into the GA
> sudo reboot
> sudo nvidia-cuda-setup --fix-kernel   # already on the GA: purge the blocked kernels
> ```
>
> It infers the phase from `uname -r`, refuses to set that boot if the GA driver does not cover the
> NIC (Case C), and asks for confirmation before purging. The steps below are the reference for what
> each one does and what to verify — and the route when the machine does not have the packages.

### Step 1: Pinning and blocking (first, always)

```bash
sudo tee /etc/apt/preferences.d/99-no-hwe-kernel >/dev/null <<'EOF'
# MongoDB 8 vs kernel 6.19-7.0.13 (SERVER-121912): stay on the GA 6.8 track
Package: linux-*hwe-24.04* linux-*hwe-7.* linux-image-7.* linux-modules-7.* linux-headers-7.* linux-tools-7.*
Pin: release *
Pin-Priority: -1
EOF

sudo tee /etc/apt/apt.conf.d/51-block-hwe-kernel >/dev/null <<'EOF'
Unattended-Upgrade::Package-Blacklist {
  "linux-generic-hwe-24.04";
  "linux-image-generic-hwe-24.04";
  "linux-headers-generic-hwe-24.04";
};
EOF

sudo apt update
```

Validate the pinning hit the right target and did **not** drag the GA track down with it:

```bash
apt-cache policy linux-generic-hwe-24.04   # expected: Candidate: (none), priority -1
apt-cache policy linux-image-generic       # expected: 500 / 6.8.0-1XX.XXX  <- must NOT be -1
```

### Step 2: Secure the GA track and remove HWE metapackages

```bash
sudo apt install --install-recommends linux-generic
sudo apt purge linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 \
                linux-headers-generic-hwe-24.04
```

`apt install linux-generic` goes **before** the purge, so the GA metapackage owns the 6.8 image and
no later `autoremove` can orphan it.

> **If the machine runs 6.9 – 6.18 and `mongod` starts**, stop here: Step 3 and the reboot are not
> needed, because the running kernel is already below the ceiling. Before the purge, protect its
> image — losing its metapackage turns it into an automatic package:
>
> ```bash
> sudo apt-mark manual linux-image-$(uname -r) linux-modules-$(uname -r) \
>                      linux-modules-extra-$(uname -r) linux-headers-$(uname -r)
> ```

> **Do not try `apt-mark hold` on those three after the purge.** It fails:
>
> ```
> E: Can't select installed nor candidate version from package 'linux-generic-hwe-24.04' as it has neither of them
> ```
>
> This is structural, not an implementation quirk: the dpkg selection is a **single field** holding
> `install` / `hold` / `deinstall` / `purge`. A purged package cannot also be held, because it is
> the same slot. And with the pin already in place there is no candidate version for `apt-mark` to
> select either.
>
> The real protection is the Step 1 pin, which is **stronger** than a hold: it leaves
> `Candidate: (none)`, meaning apt cannot install them even if asked. Verify with
> `apt-cache policy linux-generic-hwe-24.04`.
>
> A `hold` is the right tool for packages that remain installed and that you want frozen at their
> current version — `dkms`, for instance, see *Loose ends*.

### Step 3: Boot into 6.8 once

```bash
sudo grub-reboot "Advanced options for Ubuntu>Ubuntu, with Linux 6.8.0-136-generic"
sudo reboot
```

> **Careful:** `grub-reboot` is **single-use** (it writes `next_entry` in grubenv). It is not the
> fix; it is only the bridge that lets you purge 7.0 without touching the running kernel. Adjust
> `6.8.0-136-generic` to the version you actually have: check with `ls /boot/vmlinuz-6.8.0-*`.

After the reboot:

```bash
uname -r                 # 6.8.0-1XX-generic
systemctl status mongod  # active (running)
dkms status              # modules built for 6.8.0-1XX-generic
```

### Step 4: Purge kernel 7.0

**Do not use blind globs.** A glob that matches nothing makes apt abort the whole transaction
without removing anything, and the error message is easy to miss:

```
E: Couldn't find any package by glob 'linux-modules-extra-7.0.0-28*'
```

Enumerate what is actually installed first:

```bash
dpkg -l | awk '/^ii/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}'
```

Typical output (6 packages):

```
linux-headers-7.0.0-28-generic
linux-hwe-7.0-headers-7.0.0-28
linux-hwe-7.0-tools-7.0.0-28
linux-image-7.0.0-28-generic
linux-modules-7.0.0-28-generic
linux-tools-7.0.0-28-generic
```

Purge that list and **review apt's summary before confirming**: it must contain only those packages.
If anything with `6.8.0-1XX` or `nvidia-dkms-*` shows up, cancel.

```bash
sudo apt purge $(dpkg -l | awk '/^ii/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}')
sudo apt autoremove --purge
sudo update-grub
```

DKMS will unbuild the 7.0 NVIDIA module in the process. That is expected.

### Step 5: Pre-reboot verification (gate)

```bash
sudo update-grub                                       # must list only 6.8
ls /boot/vmlinuz-*                                     # a single image
sudo grub-editenv list                                 # next_entry= empty
dkms status                                            # only 6.8.0-1XX-generic
dpkg -l | awk '/^(i|h)i/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}'      # no output
sudo apt full-upgrade -s \
  | grep -E '^Inst (linux-image|linux-modules|linux-headers|linux-generic|linux-hwe)' \
  || echo "no kernel changes"
```

`update-grub` must not print any `Found linux image: /boot/vmlinuz-7.0.0-*` line.

> **Two pattern details, both hit in the field:**
>
> The last check must **not** use `grep -iE 'linux-|7\.0\.0'`: that pattern matches `linux-base`,
> `linux-firmware` and `linux-libc-dev`, which are ordinary packages, not kernels. It false-positives
> and stops a machine that is actually fine. The pattern above only looks at `Inst` lines for kernel
> packages.
>
> The second-to-last uses `^(i|h)i` rather than `^ii` because **`apt-mark hold` changes the
> `dpkg -l` state from `ii` to `hi`** (first character is the desired action, second is the actual
> state). With `^ii`, a package that is installed but held reads as absent.

> **Note:** `grep 'vmlinuz-7.0.0' /boot/grub/grub.cfg` gives *Permission denied* because `grub.cfg`
> is 0600 and `sudo` does not propagate through the pipe. Use the `update-grub` output or
> `sudo grep ... /boot/grub/grub.cfg`.

**Only with all of these checks green is the machine safe to reboot unattended.**

### Step 6: Clean up temporary mongod overrides

If a `GLIBC_TUNABLES` drop-in was added during mitigation, review it:

```bash
sudo systemctl cat mongod
```

- An override with `glibc.pthread.rseq=0` is **redundant**: the shipped unit already has it. Worse,
  when MongoDB changes that default upon releasing the fix, the override will silently shadow it.
  Remove it.
- An override with `glibc.pthread.rseq=1` was the emergency mitigation (it makes glibc win the rseq
  registration and forces TCMalloc down to per-thread caches). On kernel 6.8 it is **unnecessary**
  and degrades performance to MongoDB 7's allocator level. Remove it.

```bash
sudo rm /etc/systemd/system/mongod.service.d/override.conf
sudo rmdir /etc/systemd/system/mongod.service.d
sudo systemctl daemon-reload && sudo systemctl restart mongod
systemctl cat mongod | grep -c override.conf   # expected: 0
```

**General rule:** never edit `/usr/lib/systemd/system/mongod.service` directly — any
`mongodb-org-server` upgrade overwrites it. Always use `sudo systemctl edit mongod`.

## Case B — Provisioning New Machines

Much shorter, because 7.0 never gets installed. It is the same pinning as
[Section 3, Step 7](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version). In the autoinstall
`late-commands` (or before sealing the golden image), **in this order**:

1. Write `/etc/apt/preferences.d/99-no-hwe-kernel` and `/etc/apt/apt.conf.d/51-block-hwe-kernel`
   (identical content to Case A, Step 1) — **before any `apt install`**.
2. `apt-mark hold linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 linux-headers-generic-hwe-24.04`
3. `apt install --install-recommends linux-generic`
4. Install `mongodb-org` ([Section 6](06-compression-workstations.md)).

No GRUB step, no purge, no intermediate reboot.

> The Ubuntu **Server** ISO installs GA by default; the **Desktop** one installs HWE. If you deploy
> from Desktop, every machine is born with the problem.

## Case C — Boards whose NIC does not work on the GA kernel

Shows up with new motherboards: the Ethernet port comes up on the HWE kernel and dies when you drop
to GA 6.8. The obvious way out — installing `linux-generic-hwe-24.04`, as
[Section 9](09-network-issues.md#9-common-network-issues-with-new-motherboards) suggests — is **closed on every station
running MongoDB 8**, meaning every compression and analytics box.

What you need is not a newer kernel: it is a newer **driver**. HWE is a shortcut to get one, not the
only path.

> **Golden rule: you need network to fix the network.** If you pin to GA, reboot, and the NIC does
> not come up, you are stuck on a machine with no network that cannot download the driver that would
> fix it. The ordering in this section exists so that does not happen.

### Step 1: Identify the chip and its PCI ID, while you still have network

```bash
lspci -nn | grep -Ei 'ethernet|network'
```

Note the bracketed `vendor:device` ID — for example `10ec:8125` (Realtek RTL8125) or `8086:125c`
(Intel I226-V). Also the driver in use:

```bash
for i in /sys/class/net/e*; do
  n=$(basename "$i")
  echo "$n -> $(basename "$(readlink -f "$i/device/driver")" 2>/dev/null)"
done
```

### Step 2: Install the GA kernel without rebooting

Apply the pin from Case A Step 1, then:

```bash
sudo apt install --install-recommends linux-generic
```

This brings in the GA modules. Where each driver actually lives, verified against the 6.8.0-137
packages:

| Package | Ethernet drivers it contains |
|---|---|
| `linux-modules-6.8.0-1XX-generic` | `e1000e`, `igb`, `ixgbe`, `i40e`, `8139too`… |
| `linux-modules-extra-6.8.0-1XX-generic` | **`r8169`**, **`igc`**, `atlantic`, and the rest |

The two that matter for this problem — `r8169` (Realtek) and `igc` (Intel I225/I226) — live in
`linux-modules-extra`. They arrive either way: `linux-image-generic` **depends** on it, it does not
merely recommend it. But if you are hunting for the file by hand, that is where it is, not in
`linux-modules`.

### Step 3: Ask the GA driver whether it knows your board

Still without rebooting:

```bash
# The target kernel is the newest compatible one (< 6.19) that is installed,
# not 6.8 as such: if the machine already has a 6.14, that is where it boots.
KDEST=$(ls /lib/modules | awk -F. '$1 == 6 && $2 < 19' | sort -V | tail -1)
DRV=igc                  # or e1000e, igb, r8169 per Step 1
ID=8086:125c             # the PCI ID from Step 1

ALIAS="pci:v0000$(echo "${ID%:*}" | tr 'a-f' 'A-F')d0000$(echo "${ID#*:}" | tr 'a-f' 'A-F')"
modinfo -k "$KDEST" "$DRV" | grep -qi "$ALIAS" \
  && echo "OK: the $KDEST driver knows $ID" \
  || echo "MISSING: the $KDEST driver does not declare $ID"
```

`modinfo -k` queries **another** kernel's module, so it works before booting it. It requires that
kernel's `linux-modules-extra-*` to be installed, which is what Step 2 did.

> **This check is useless for Realtek 2.5GbE.** The GA's `r8169` declares its alias with a
> revision wildcard:
>
> ```
> alias: pci:v000010ECd00008125sv*sd*bc*sc*i*     (6.8.0-137, linux-modules-extra)
> ```
>
> It matches revisions A, B, C and D, but the code only handles up to C. With an **RTL8125D** it
> claims the device and only then gives up:
>
> ```
> r8169 0000:07:00.0: unknown chip XID 688
> ```
>
> So the command above prints **OK** and the interface still will not come up. For `10ec:8125` go
> straight to Step 4: no prior check rules it out, and installing the driver you did not strictly
> need costs nothing.

| Result | Path |
|---|---|
| `10ec:8125` (any revision) | Step 4 always — the alias proves nothing |
| **OK** for anything else | GA supports the board. Normal Case A from Step 3 |
| **MISSING** | Step 4 **before** rebooting |

### Step 4: Bring the driver in via DKMS, with the network still alive

DKMS is the right answer because it **rebuilds the module on every kernel change**, so it survives
GA-series updates. `/etc/kernel/postinst.d/dkms` triggers it when a kernel is installed, and one
module ends up built for every kernel present.

**Realtek 2.5GbE (`10ec:8125`).** Ubuntu's own `r8125-dkms` is **not enough**. noble ships
9.011.00, whose hardware detection switch covers `0x60800000`, `0x64000000` and `0x64800000`
(CFG_METHOD_2 through 8) and sends anything else to `default: unknown chip version`. XID 688 is
`0x68800000`: it lands there. The source never mentions the 8125D — only A, B and C.

You need the vendor driver, **version 9.014.01 or newer**, packaged for DKMS:

```bash
sudo apt install -y dkms build-essential "linux-headers-$GA"

# If Ubuntu's package is installed, remove it: two modules claiming 10ec:8125
sudo apt purge -y r8125-dkms

VER=9.016.01-1
wget "https://github.com/awesometic/realtek-r8125-dkms/releases/download/${VER}/realtek-r8125-dkms_${VER}_amd64.deb"
sudo dpkg -i "realtek-r8125-dkms_${VER}_amd64.deb"
```

The `postinst` builds for the **running** kernel (the HWE), and that build may fail against a newer
kernel's APIs. It does not matter: on the HWE the in-tree `r8169` already handles the 8125D. The
only critical part is that it gets built for GA, which you force separately:

```bash
sudo dkms install realtek-r8125/9.016.01 -k "$GA" --force
```

> **Do not blacklist `r8169`.** The vendor package sometimes does it for you, and that kills
> RTL8168/8111 NICs (`10ec:8168`), which depend on it — on dual-port boards that is often the only
> working link. It is unnecessary, and the real mechanism is not `depmod`'s search order: both
> modules declare the `10ec:8125` alias, `modprobe` loads both, and the device goes to whichever
> probes successfully first. `r8169` ships in the initramfs and gets there earlier — measured in the
> field, `r8169` at 0.8 s and `r8125` at 3.4 s — so it keeps the revisions it supports and `r8125`
> stays loaded but unused, harmlessly. On the 8125D it fails the probe, releases the device, and
> `r8125` takes it.
>
> **This is why verification is by bound driver, not by loaded module:**
>
> ```bash
> ethtool -i enp5s0 | head -2      # driver: r8125 if r8169 rejected the card
> lsmod | grep -E 'r8169|r8125'    # both may be loaded: proves nothing
> ```
>
> ```bash
> grep -rl 'blacklist[[:space:]]\+r8169' /etc/modprobe.d/   # if it returns anything, delete that line
> ```

**Intel `igc` (I225/I226).** There is no DKMS package in the repos: you have to build from the
source Intel publishes in its Download Center and wrap it in DKMS. More work, which is why the two
hardware alternatives usually win on time:

- **Intel I210 or I350 PCIe NIC.** Solid on GA 6.8, no DKMS to maintain. Cheapest option measured
  in operating hours.
- **USB Ethernet adapter.** Immediate. Check that it supports Wake-on-LAN if that station needs it,
  because many do not.

If there is no network at all to download the DKMS package, use USB tethering from a phone or carry
the `.deb` and its dependencies on a USB stick.

> If you are provisioning with the project's `.deb` packages, `nic-driver-rescue` does this whole
> step. It ships inside `nvidia-cuda-setup`, `workstation-compression` and `workstation-analytics`. It detects the
> NIC, removes the old `r8125-dkms`, fetches the vendor one, builds for GA, strips the blacklist and
> verifies. With `--deb PATH` or `--no-download` it works offline.

### Step 5: Verify the module got built for GA

**Before rebooting** — this is what decides whether it is safe to. `dkms status` is the first step
but not enough:

```bash
dkms status
sudo dkms autoinstall     # if it does not list the module for GA
```

What actually loads the driver at boot is `udev` consulting `modules.alias`. Check the file, **its
version** and the index, in that order:

```bash
sudo depmod -a "$GA"

# 1. The .ko exists, and it is under updates/ (which is what beats the in-tree one)
KO=$(find "/lib/modules/$GA/updates" -name 'r8125.ko*' -print -quit)
echo "${KO:-NO MODULE}"

# 2. And it is the vendor one, not noble's 9.011.00
modinfo -F version "$KO"          # must be >= 9.014.01

# 3. udev will find it by alias
awk '$1=="alias" && index($2,"pci:v000010ECd00008125")==1 {print $3}' \
    "/lib/modules/$GA/modules.alias"
```

The first must return a path, the second a version **9.014.01 or higher**, and the third must
include `r8125`. If the `find` comes back empty, **do not reboot**: the machine will come up with
no network.

> **Step 2 is not optional, and it was missing from this guide for a while.** noble's `r8125-dkms`
> 9.011.00 also drops an `r8125.ko` under `updates/dkms/`, so step 1 returns a path and everything
> looks fine — but that driver still sends XID 688 to `unknown chip version`. It is the most
> expensive **false green** in this runbook: the check passes, you reboot, and the rev D board comes
> up with no network. If the version is below 9.014.01, treat it as **MISSING** and go back to
> Step 4.

> Do not use `modinfo -k "$GA" r8125` for this. In `/lib/modules` trees created only by DKMS, with
> no kernel package, `modinfo` by name gives false negatives. Verify by file.

### Step 6: Only now, boot into GA

Use a **one-shot** boot instead of changing the default. If the network does not come up, the next
reboot returns to the previous kernel on its own and you keep your access:

```bash
sudo grub-reboot "Advanced options for Ubuntu>Ubuntu, with Linux $GA"
sudo reboot
```

Once up, add the network to the Case A Step 5 gate, before purging the old kernel:

```bash
ip -br link show                 # the Ethernet interface in UP state
ethtool -i enp5s0 | head -2      # WHICH driver got bound, not which one is loaded
ping -c 3 archive.ubuntu.com
```

With the network validated, only then pin GA as the permanent default:

```bash
sudo sed -i "s|^GRUB_DEFAULT=.*|GRUB_DEFAULT=\"Advanced options for Ubuntu>Ubuntu, with Linux $GA\"|" /etc/default/grub
sudo update-grub
```

**Do not purge the HWE kernel until the network works on GA.** While it stays installed you have a
rescue boot; the pin stops it from being reinstalled, but does not delete what is already there.

## Ansible Preflight for the Fleet

Add this as the first task of the fleet plays, so a badly provisioned machine fails loudly on the
console instead of breaking silently in the field:

```yaml
- name: Kernel incompatible con MongoDB 8 (SERVER-121912)
  ansible.builtin.assert:
    that:
      - ansible_kernel is version('6.19', '<')
    fail_msg: >-
      {{ inventory_hostname }} corre {{ ansible_kernel }}: el rango 6.19-7.0.13
      bloquea el arranque de mongod. Aplicar el runbook (Caso A) antes de continuar.
    success_msg: "Kernel {{ ansible_kernel }} OK para MongoDB 8"
```

On individual machines the same control is done by the doctor scripts from
[Section 12](12-doctor-scripts.md#12-doctor-verification-scripts) via the *Kernel compatible con MongoDB 8* check.

## Loose Ends

- **THP:** MongoDB 8.0 requires Transparent Huge Pages **enabled** — the opposite of 7.0 and
  earlier. If an old provisioning script carries `transparent_hugepage=never` in
  `GRUB_CMDLINE_LINUX` or a systemd unit that disables it, remove it.
- **Numeric `GRUB_DEFAULT`:** do not use indexes (`"1>2"`). They shift with every installed kernel
  and the machine ends up booting something else weeks later. With 7.0 purged, GRUB picks 6.8 on its
  own and nothing needs pinning.
- **Third-party dkms:** on `test-workstation` the `dkms` package comes from the local CUDA repo
  (`dkms/unknown 1:3.2.1-1ubuntu2`) instead of noble's. Mixing versions can complicate NVIDIA module
  rebuilds on the next kernel change. If modules fail to rebuild, that is the first suspect.
  Consider `apt install dkms=3.0.11-1ubuntu13` + hold, unless CUDA 13 requires otherwise.

## Exit Criteria (When to Revert This)

This runbook is a mitigation, not an end state. Review
[SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912) periodically.

Conditions for reopening the HWE lane:

1. MongoDB ships a release with patched TCMalloc and confirms it in the release notes / production
   notes (today they only say it will be resolved "as soon as a patched version of TCMalloc is
   available").
2. Validate on **one** lab machine: install HWE, check `/proc/version_signature`, confirm `mongod`
   starts **and stays alive for several minutes** (there was a failure mode with SIGSEGV at 30-60 s
   from Shadow Stacks / CET on Zen 5 CPUs, distinct from the rseq bug).
3. Only then: remove the pinning, the holds, the unattended-upgrades blacklist, and the doctor
   script check, and update this section.

## Troubleshooting

- **`apt purge` aborts with `Couldn't find any package by glob ...`:** Nothing was removed.
  Enumerate with the `dpkg -l | awk ...` from Step 4 and purge the real list.
- **`apt-cache policy linux-image-generic` shows `-1`:** The pin was too wide and blocked the GA
  track. Review the `Package:` line in `/etc/apt/preferences.d/99-no-hwe-kernel`.
- **The machine went back to 7.0 after reboot:** `grub-reboot` is single-use. Repeat Step 3 and do
  not reboot again until Steps 4 and 5 are done.
- **NVIDIA modules do not rebuild on 6.8:** `sudo dkms autoinstall && dkms status`. If it still
  fails, check the `dkms` version (see *Loose Ends*) and reinstall the `.run` driver from
  [Section 4](04-nvidia-drivers.md#4-installing-nvidia-drivers-on-ubuntu).
- **`mongod` starts and dies after 30-60 s with SIGSEGV:** Not this bug. That is Shadow Stacks / CET
  on Zen 5 CPUs, a different failure mode.

---

> [Index](../../README_en.md#index) · [Previous: 13. Security Best Practices (Optional)](13-security.md) · [Next: FAQ: Frequently Asked Questions](15-faq.md) · [Español](../14-runbook-mongodb8-kernel.md)
