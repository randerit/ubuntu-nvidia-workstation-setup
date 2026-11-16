# 5. Installing CUDA Toolkit

> [Index](../../README_en.md#index) · [Previous: 4. Installing NVIDIA Drivers on Ubuntu](04-nvidia-drivers.md) · [Next: 6. Specific Setup for Compression Workstations](06-compression-workstations.md) · [Español](../05-cuda-toolkit.md)

> **Note:** This section installs CUDA Toolkit only, using NVIDIA's `.deb (local)` installer. It assumes the NVIDIA driver is already installed via `.run` (section 4). **Do not install the `cuda` or `cuda-drivers` meta-packages**: both pull in NVIDIA's packaged driver and would override your `.run` install. Install only `cuda-toolkit-XX-Y`.

> **Version pinned by this manual:** **CUDA 13.0** (compatible with the 580.x.x driver branch). If you switch versions, adjust the commands and paths (`13-0` → `XX-Y`, `cuda-13.0` → `cuda-XX.Y`).

## Before starting

Confirm:

- NVIDIA `.run` driver 580.x.x already installed (section 4) and `nvidia-smi` works.
- Internet available.
- No previous CUDA install via APT, snap, or `.run` from another version.

## Step 1: CUDA repository pin

The pin ensures correct priority when packages overlap with other repos:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-ubuntu2404.pin
sudo mv cuda-ubuntu2404.pin /etc/apt/preferences.d/cuda-repository-pin-600
```

> **Side effect of the pin:** its last rule is `Package: *` with `Pin-Priority: 600`, so
> **everything** NVIDIA publishes outranks `noble`, including the `dkms` they repackage (it shows
> up as `dkms/unknown 1:3.2.1-1ubuntu2` in `apt list --upgradable`). The driver module is built by
> that `dkms`, so swapping it for an out-of-distro build is not worth it. A pin by package name
> beats the wildcard and hands `dkms` back to Ubuntu, which keeps getting its security updates:
>
> ```bash
> sudo tee /etc/apt/preferences.d/99-dkms-desde-ubuntu >/dev/null <<'EOF'
> Package: dkms
> Pin: release l=NVIDIA CUDA
> Pin-Priority: -1
> EOF
> apt-cache policy dkms    # Candidate must be noble's, not 1:3.2.1
> ```
>
> Installers 2.3.1+ write this pin themselves when they apply the CUDA one.

## Step 2: Download and install the local CUDA 13.0 repository

```bash
wget https://developer.download.nvidia.com/compute/cuda/13.0.0/local_installers/cuda-repo-ubuntu2404-13-0-local_13.0.0-580.65.06-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2404-13-0-local_13.0.0-580.65.06-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2404-13-0-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
```

> **Important — do not change versions in this step.** The `.deb` filename changes with each release
> (`13.0.0-580.65.06-1` here) and may eventually stop being published at that path.
>
> If the `wget` fails, do **not** go to [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
> and copy the commands it shows: that page always serves the **latest** release, not 13.0. Its
> commands install a different `cuda-toolkit-XX-Y`, which contradicts the pin declared at the top of
> this same section and moves the `/usr/local/cuda` symlink to the newer version (see Step 4). The
> machine ends up with two toolkits and with `nvcc` saying one thing in your shell and another under
> `sudo`: that is what `workstation-doctor-analitica` / `workstation-doctor-compresion` fail on, in the
> check `CUDA Toolkit coherente` (the doctors print in Spanish).
>
> The 13.0 local installer lives in the archive:
> [https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive)
> -> CUDA Toolkit 13.0.0 -> Linux > x86_64 > Ubuntu > 24.04 > deb (local).
>
> Changing the pinned version is a manual-wide decision, not a decision for this step: it also means
> touching Step 4, `CUDA_VERSION_EXPECTED` in `doctor_lib.sh`, and `CUDA_VERSION` in the `.deb`
> installers.
>
> **If the machine already came with a different version installed** (it happens: the download page
> always serves the latest), there is no need to downgrade it. Since 2.9.0 the `.deb` installer
> adopts whichever it finds, and the doctors validate **coherence** — that `nvcc`, the symlink and
> `dpkg` all point at the same version — not the number itself. What is not accepted is a machine
> with two toolkits and the sources disagreeing.

## Step 3: Install the toolkit only (no driver)

```bash
sudo apt-get -y install cuda-toolkit-13-0
```

> **Do not run** `sudo apt-get install cuda` or `sudo apt-get install cuda-drivers`. Those packages install NVIDIA's packaged driver and break the `.run` 580.x.x driver from section 4.

**Verification (optional):**
```bash
dpkg -l | grep cuda-toolkit-13-0
ls /usr/local/cuda-13.0/bin/nvcc
```

## Step 4: Pin the CUDA symlink and configure PATH and LD_LIBRARY_PATH

NVIDIA's packages register `/usr/local/cuda` with `update-alternatives` using a version-derived
priority: if the machine ever had another toolkit, the newer one wins on its own and nothing puts it
back. Pin it to the manual's version:

```bash
sudo update-alternatives --set cuda /usr/local/cuda-13.0
```

> **Why it matters:** the `workstation-doctor-*` scripts run under `sudo`, and `sudo` does not read your
> `~/.bashrc`. The `nvcc` the doctor sees is the one behind this symlink, not the one on your
> interactive PATH. A machine with a correct `.bashrc` and a symlink pointing elsewhere still reports
> `[FALLO]`.

Now edit `~/.bashrc`:

```bash
nano ~/.bashrc
```

Add at the end:

```bash
export PATH=/usr/local/cuda-13.0/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

Save and reload:

```bash
source ~/.bashrc
```

**Verification:**
```bash
readlink -f /usr/local/cuda   # /usr/local/cuda-13.0
which nvcc                # /usr/local/cuda-13.0/bin/nvcc
nvcc --version            # release 13.0
/usr/local/cuda/bin/nvcc --version   # what the doctor sees (without your PATH): release 13.0
nvidia-smi                # 580.x.x driver still loaded
```

## If you need to uninstall CUDA Toolkit

```bash
sudo apt-get -y remove --purge 'cuda-toolkit-13-0' 'cuda-*-13-0'
sudo apt-get -y autoremove
sudo rm -rf /usr/local/cuda-13.0
sudo rm -f /etc/apt/preferences.d/cuda-repository-pin-600
sudo rm -f /etc/apt/sources.list.d/cuda-ubuntu2404-13-0-local.list
sudo apt-get update
```

This does not touch the NVIDIA `.run` driver.

## CUDA Troubleshooting

- **`nvcc: command not found`:** check `~/.bashrc` has the `export PATH=...` line and that you ran `source ~/.bashrc`.
- **The doctor reports `[FALLO] CUDA Toolkit coherente` but your `nvcc --version` says 13.0:** the doctor runs under `sudo` and reads `/usr/local/cuda`, not your `~/.bashrc`. Compare with `readlink -f /usr/local/cuda` and apply the `update-alternatives --set` from Step 4. The doctor prints all three sources (nvcc, symlink and dpkg) in the message, so you can see which one disagrees.
- **The machine has CUDA 13.1 or 13.4 instead of 13.0:** not an error by itself. The doctor reports it with `[INFO]` and only fails when the sources disagree; the 2.9.0+ `.deb` installer adopts that version instead of downloading another ~5 GB. If you do want the pinned one: `sudo nvidia-cuda-setup --cuda-version 13.0`.
- **You have two toolkits installed (`ls -d /usr/local/cuda-*` shows more than one):** someone followed the commands from NVIDIA's download page instead of Step 2. No purge needed: pinning the symlink from Step 4 is enough. To reclaim the space (~5 GB per toolkit), review `sudo apt-get -s purge 'cuda-toolkit-XX-Y' 'cuda-*-XX-Y'` before running it without `-s`.
- **`apt` wants to install `nvidia-driver-*` or `cuda-drivers-*`:** you are calling the `cuda` meta-package. Use only `cuda-toolkit-13-0`.
- **Driver stopped working after installing CUDA:** you installed `cuda` or `cuda-drivers`. Purge with the uninstall section, reinstall the `.run` driver (section 4), and reinstall only `cuda-toolkit-13-0`.
- **`nvidia-smi` and `nvcc` report different versions:** this is normal. `nvidia-smi` shows the driver version, `nvcc` shows the toolkit version.

---

> [Index](../../README_en.md#index) · [Previous: 4. Installing NVIDIA Drivers on Ubuntu](04-nvidia-drivers.md) · [Next: 6. Specific Setup for Compression Workstations](06-compression-workstations.md) · [Español](../05-cuda-toolkit.md)
