# 1. Pre-Installation Requirements

> [Index](../../README_en.md#index) · [Previous: Introduction](00-introduction.md) · [Next: 2. Ubuntu System Installation](02-ubuntu-installation.md) · [Español](../01-requisitos-previos.md)

## Before touching the machine

Confirm these points before installing Ubuntu:

| You need | Why |
|----------|-----|
| USB drive of 8 GB or more | To boot the Ubuntu installer. |
| Ubuntu Desktop LTS ISO image | This is the file copied to the USB drive. This guide uses Ubuntu Desktop 24.04 LTS as reference. |
| Backup of important data | The installation can erase the entire disk. |
| Internet access | Helps install updates and packages during the process. |
| Workstation type defined | Decide if the machine will be used for **compression/data** or **analytics**. |

> **Important alert:** If the machine has files you cannot lose, back them up before continuing. The simple installation path uses "Erase disk and install Ubuntu".

## Quick decision

- If the machine will be used by a person and has a screen, install **Ubuntu Desktop**.
- If the machine will be managed remotely, you can still start with **Ubuntu Desktop** and disable the graphical interface later.
- If you need dual boot with Windows, do not use the simple path in this section; it requires manual partitioning.

## Ubuntu and direct derivatives (Linux Mint)

This manual targets Ubuntu LTS, and it also applies to direct derivatives that repackage
Ubuntu without changing the base: **Linux Mint 21.x (22.04 base)** and **Linux Mint 22.x
(24.04 base)**. What matters is the base, not the distro's own version number: Mint 22.1 is not
Ubuntu 22.04, it is Ubuntu 24.04 repackaged. Check the base with:

```bash
cat /etc/upstream-release/lsb-release
```

It must say `DISTRIB_ID=Ubuntu` and `DISTRIB_RELEASE=24.04` (or `22.04`). If the file is
missing, read `UBUNTU_CODENAME` from `/etc/os-release` (`noble` = 24.04, `jammy` = 22.04).

> **Never use `lsb_release -cs` on a derivative.** On Mint it returns Mint's own codename
> (`wilma`, `xia`, `virginia`), which does not exist in the Ubuntu, NVIDIA, MongoDB or EMQX
> repositories: any repo built from that value returns 404. Always use `noble` or `jammy`,
> whichever matches the base.

Three Mint differences that do change steps in this manual:

| Difference | What it means |
|-----------|---------------|
| `/etc/apt/preferences.d/nosnap.pref` blocks `snapd` | With that pin (`-10`) `apt` leaves `snapd` with no candidate, so the snap steps (Go, VS Code) cannot run. To enable them: `sudo cp -a /etc/apt/preferences.d/nosnap.pref /var/backups/nosnap.pref.bak && sudo rm /etc/apt/preferences.d/nosnap.pref && sudo apt-get update`. Reverting is a `mv` of the backup. Installers 2.5.0+ and `workstation-doctor-compresion --fix` do this on their own, unless `--skip-snaps` is given. |
| The session manager is LightDM, not GDM | `/etc/gdm3/custom.conf` tweaks (such as disabling Wayland) do not apply: Mint already runs X11 with Cinnamon. To turn the graphical interface off, use `lightdm` instead of `gdm3`. |
| Mint's Update Manager offers kernels | If you pinned the kernel because of MongoDB 8, do not install kernels from there; the `apt` pin does not cover anything installed by hand. The 6.14 that ships with Mint 22.2 is compatible and does **not** need to go down to 6.8. |

LMDE (Linux Mint Debian Edition) is **not** supported: its base is Debian, not Ubuntu, and the
installers reject it.

---

> [Index](../../README_en.md#index) · [Previous: Introduction](00-introduction.md) · [Next: 2. Ubuntu System Installation](02-ubuntu-installation.md) · [Español](../01-requisitos-previos.md)
