# 2. Ubuntu System Installation

> [Index](../../README_en.md#index) · [Previous: 1. Pre-Installation Requirements](01-requirements.md) · [Next: 3. Initial Ubuntu System Preparation](03-system-preparation.md) · [Español](../02-instalacion-ubuntu.md)

This section leaves Ubuntu installed and ready for initial preparation. Follow the steps in order.

## Step 1: Download Ubuntu

1. Go to [https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop).
2. Download the **Ubuntu Desktop LTS** version indicated for your installation.
3. Save the `.iso` file somewhere easy to find, for example `Downloads`.

> **If the machine will run MongoDB 8:** Ubuntu Desktop 24.04.4 and later ISOs install the
> **HWE 7.0** kernel, which prevents `mongod` from starting (see
> [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70)). The Ubuntu **Server** ISO
> installs the GA track by default and does not have this problem. If you install from Desktop
> anyway, apply the preventive pinning in
> [Section 3, Step 7](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version) before installing MongoDB.

## Step 2: Create the installation USB

The simplest option is to use a graphical tool:

1. Download BalenaEtcher from [https://etcher.balena.io/](https://etcher.balena.io/) or Ventoy from [https://www.ventoy.net/](https://www.ventoy.net/).
2. Connect the USB drive.
3. Select the Ubuntu ISO.
4. Select the correct USB drive.
5. Start the process and wait until it finishes.

> **Careful:** The tool will erase the USB drive. Check twice that you selected the correct drive.

## Step 3: Enter BIOS/UEFI

1. Shut down the machine.
2. Connect the USB drive.
3. Turn on the machine and press the BIOS key several times.

Common keys: `DEL`, `F2`, `F8`, `F10`, `F11`, `F12`, or `ESC`.

Common examples:

- ASUS usually uses `DEL`.
- MSI usually uses `DEL` or `F2`.
- Gigabyte usually uses `DEL`.

If it does not enter BIOS, restart and try another key.

## Step 4: Adjust BIOS/UEFI

Inside BIOS, change only what is needed:

| Option | Recommended value | Reason |
|--------|-------------------|--------|
| Secure Boot | Disabled | Prevents conflicts with proprietary NVIDIA drivers. |
| Boot Priority | USB first | Allows the Ubuntu installer to boot. |
| AC Power Loss | Always On, if it is a remote workstation | The machine powers back on after a power outage. |

Save changes with `F10` or with the **Save and Exit** option.

## Step 5: Boot from the USB

1. After restarting, choose the USB drive as the boot device.
2. Select **Try or Install Ubuntu**.
3. Wait for the installer to load.

If a black screen appears before entering the installer, use `nomodeset`:

1. In the boot menu, press `E`.
2. Find the line that starts with `linux`.
3. Add `nomodeset` at the end of that line.
4. Press `F10` to continue.

**Example edited line:**
```
linux /boot/vmlinuz-... nomodeset ---
```

## Step 6: Install Ubuntu with simple options

In the installer, use this selection:

| Screen | Recommended selection |
|--------|-----------------------|
| Language | **English**, to keep standard folder names like `Desktop` and `Downloads`. |
| Keyboard | Spanish or the physical keyboard layout. |
| Network | Connected to the internet if possible. |
| Installation type | Normal installation. |
| Additional software | Install updates if the installer offers them. If "third-party software" mixes graphics and Wi-Fi, leave it unchecked; network drivers are reviewed in section 3 and NVIDIA is installed later with `.run`. |
| Disk | **Erase disk and install Ubuntu**, only if you already backed everything up. |
| User | Create a normal user with a strong password. |
| Time zone | Select the correct time zone. |

> **Important alert:** `Erase disk and install Ubuntu` erases the selected disk. Do not choose this option if you need to keep Windows, partitions, or files.

The installation can take between 15 and 30 minutes. When it finishes, the installer will ask you to restart.

## Step 7: First boot

1. When Ubuntu asks, remove the USB drive.
2. Press `Enter` if the restart message appears.
3. Log in with the user you created.
4. Open a terminal with `Ctrl+Alt+T`.
5. Run these basic checks:

```bash
lsb_release -a
ping -c 4 google.com
df -h
```

Expected result:

- `lsb_release -a` shows Ubuntu.
- `ping` receives replies.
- `df -h` shows available disk space.

## If something fails during installation

| Problem | What to try first |
|---------|-------------------|
| The USB does not appear at boot | Recreate the USB, try another USB port, or check boot order. |
| Black screen before the installer | Boot with `nomodeset`. |
| The installer freezes | Restart, disable overclock in BIOS, and try again. |
| You cannot disable Secure Boot | Check the motherboard manual or search the exact BIOS model. |
| Error erasing or preparing the disk | Use the simple option if you do not need dual boot; if you need dual boot, stop and prepare partitions manually. |
| No internet | Continue the installation and solve networking later in the network issues section. |

---

> [Index](../../README_en.md#index) · [Previous: 1. Pre-Installation Requirements](01-requirements.md) · [Next: 3. Initial Ubuntu System Preparation](03-system-preparation.md) · [Español](../02-instalacion-ubuntu.md)
