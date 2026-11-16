# 4. Installing NVIDIA Drivers on Ubuntu

> [Index](../../README_en.md#index) · [Previous: 3. Initial Ubuntu System Preparation](03-system-preparation.md) · [Next: 5. Installing CUDA Toolkit](05-cuda-toolkit.md) · [Español](../04-drivers-nvidia.md)

This section installs the official NVIDIA driver using the `.run` file. This is the main method in this manual.

## Before starting

Confirm that you already completed section 3:

- Ubuntu is updated.
- Networking works.
- `gcc`, `dkms`, and kernel headers are installed.
- Secure Boot is disabled in BIOS/UEFI.
- You did not install NVIDIA through "Additional Drivers", `ubuntu-drivers`, or APT.

> **Important:** Do not mix methods. If you install NVIDIA with `.run`, do not later install `nvidia-driver-XXX`, `nvidia-open`, or `cuda-drivers` with APT on top of the same installation.

## Recommended branch: 580.x.x

For these workstations, we use the **R580 / 580.x.x** family because it has been the most stable in our testing. When downloading the driver, look for the newest available 580 version for your GPU.

Do not switch to another driver family only because a newer version exists. Change branches only for a concrete reason: support for a new GPU, a critical bug fix, or internal validation.

## Step 1: Identify the NVIDIA GPU

Run:

```bash
lspci -nn | grep -Ei 'nvidia|vga|3d|display'
```

Example:

```
01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3070] (rev a1)
```

If no NVIDIA GPU appears:

- Check that the GPU is physically installed correctly.
- Check BIOS/UEFI.
- Do not continue with the `.run` until the system detects the GPU.

## Step 2: Download the `.run` driver

1. Go to [https://www.nvidia.com/drivers/](https://www.nvidia.com/drivers/).
2. Select your exact GPU model.
3. Select **Linux 64-bit** as the operating system.
4. Look for a **580.x.x** version.
5. Download the `.run` file.
6. Save it in `Downloads`.

If NVIDIA offers several options, prefer the newest 580 family version compatible with your GPU. If the website does not offer 580 for that model, stop and review compatibility before installing another family.

In the terminal, confirm the file exists:

```bash
cd ~/Downloads
ls NVIDIA-Linux-x86_64-*.run
mv NVIDIA-Linux-x86_64-*.run NVIDIA-driver.run
```

If `mv` fails because there is more than one `.run`, leave only the driver you will install in `Downloads` and repeat the command.

If NVIDIA publishes a checksum for your download, compare it:

```bash
sha256sum NVIDIA-driver.run
```

## Step 3: Clean previous NVIDIA installations

On a freshly installed machine there should not be much to clean, but this avoids mixing methods:

```bash
dpkg -l | grep -Ei 'nvidia|cuda-drivers' || true
sudo apt purge -y '^nvidia-.*' '^libnvidia-.*' '^cuda-drivers.*' '^nvidia-open.*'
sudo apt autoremove -y
```

If the command removes anything, reboot before continuing:

```bash
sudo reboot
```

## Step 4: Disable Nouveau and enter text mode

`nouveau` is the open driver that Ubuntu may load before NVIDIA is installed. The `.run` installer needs it inactive.

```bash
printf 'blacklist nouveau\noptions nouveau modeset=0\n' | sudo tee /etc/modprobe.d/blacklist-nouveau.conf
sudo update-initramfs -u
sudo systemctl set-default multi-user.target
sudo reboot
```

After reboot you will see a text console. Log in with your user and verify:

```bash
lsmod | grep nouveau
```

Expected result: no output. If `nouveau` appears, do not continue; repeat this step and reboot.

## Step 5: Run the `.run` installer

From the text console:

```bash
cd ~/Downloads
chmod +x NVIDIA-driver.run
sudo ./NVIDIA-driver.run --dkms
```

Answer like this if the installer asks:

| Installer question | Recommended answer |
|--------------------|--------------------|
| `The distribution-provided pre-install script failed...` | `Yes`, continue. On Ubuntu this is often a warning. |
| Register modules with DKMS | `Yes`. This helps when the kernel changes. |
| Module type: Open/MIT-GPL or Proprietary | For RTX 20/30/40/50 or newer, use Open/MIT-GPL if shown. For older pre-Turing GPUs, use Proprietary. If unsure, leave the option recommended by the installer. |
| 32-bit libraries | `No`, unless you need old 32-bit applications. |
| Run `nvidia-xconfig` | `No`. |

If it fails, review:

```bash
less /var/log/nvidia-installer.log
```

## Step 6: Return to graphical mode and reboot

When the installer finishes successfully:

```bash
sudo systemctl set-default graphical.target
sudo reboot
```

## Step 7: Verify the NVIDIA driver

After reboot, open a terminal and run:

```bash
nvidia-smi
cat /proc/driver/nvidia/version
dkms status | grep -i nvidia
```

Expected result:

- `nvidia-smi` shows the GPU.
- `/proc/driver/nvidia/version` shows the loaded version.
- `dkms status` shows the NVIDIA module installed for the current kernel.

You can also save a machine summary:

```bash
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
```

## If you need to uninstall the `.run`

Use this only if the driver was installed incorrectly or you need to start over:

```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

Then log in through the console and run:

```bash
sudo nvidia-uninstall
sudo rm -f /etc/modprobe.d/blacklist-nouveau.conf
sudo update-initramfs -u
sudo systemctl set-default graphical.target
sudo reboot
```

## If something fails with NVIDIA

| Problem | What to check first |
|---------|---------------------|
| `nvidia-smi` says it failed | Check Secure Boot, reboot, and inspect `/var/log/nvidia-installer.log`. |
| The installer says `nouveau` is active | Repeat step 4, run `sudo update-initramfs -u`, and reboot. |
| Module compilation fails | Check `gcc --version`, `dkms status`, and `ls /usr/src/linux-headers-$(uname -r)`. |
| Black screen after reboot | Enter recovery mode or TTY, run `sudo nvidia-uninstall`, and retry. |
| It broke after a kernel update | Install headers for the new kernel and run `sudo dkms autoinstall`. |
| You installed through APT by mistake | Purge NVIDIA packages with APT, reboot, and repeat this section from step 3. |

Official references:

- [NVIDIA Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/)
- [NVIDIA Driver Downloads](https://www.nvidia.com/drivers/)

---

> [Index](../../README_en.md#index) · [Previous: 3. Initial Ubuntu System Preparation](03-system-preparation.md) · [Next: 5. Installing CUDA Toolkit](05-cuda-toolkit.md) · [Español](../04-drivers-nvidia.md)
