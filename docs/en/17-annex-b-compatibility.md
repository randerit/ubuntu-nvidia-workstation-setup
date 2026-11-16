# Annex B: Compatibility Verification

> [Index](../../README_en.md#index) · [Previous: Annex A: Identifying NVIDIA GPUs](16-annex-a-nvidia-gpus.md) · [Next: Annex C: Kernel Compatibility Matrix (Ubuntu 24.04 LTS)](18-annex-c-kernel-matrix.md) · [Español](../17-anexo-b-compatibilidad.md)

> **Note:** Before installing drivers or CUDA, verify compatibility to avoid errors. Use commands to check installed versions. If incompatibilities, update or downgrade as needed.

## Check Installed Versions
Run these commands to confirm your current setup:

### NVIDIA Driver
```bash
nvidia-smi  # Shows driver version, CUDA runtime, GPU
# Example output: Driver Version: 580.159.03
```

### CUDA Toolkit
```bash
nvcc --version  # CUDA compiler version
# If not installed: "Command 'nvcc' not found"
```

### Ubuntu Kernel and GCC
```bash
uname -r  # Kernel version (e.g., 6.8.0-40-generic)
gcc --version | head -1  # GCC version (e.g., gcc 11.4.0)
```

## Recommended Compatibility (May 2026)
Based on NVIDIA docs and internal validation. For this manual, the standard combo is **driver 580.x.x (`.run`) + CUDA Toolkit 13.0 (`.deb local`)**.

### NVIDIA Drivers and GPUs
| GPU Series | Architecture | Approximate technical minimum | Manual recommended branch |
|-----------|--------------|-------------------------------|---------------------------|
| RTX 3000 (Ampere) | GA10x | 470.x | 580.x.x |
| RTX 4000 (Ada Lovelace) | AD10x | 525.x | 580.x.x |
| RTX 5000 (Blackwell) | GB20x | 570.x/580.x depending on model | 580.x.x |

**Note:** Install the newest available 580 family version for your GPU. Do not change branches without validating first.

### CUDA Toolkit and Drivers
| CUDA Toolkit | Recommended minimum driver | Ubuntu Support | Status in this manual |
|--------------|----------------------------|----------------|-----------------------|
| 13.0 | 580.65.06 | 22.04, 24.04 | **Pinned version** |
| 12.8 | 570.x | 22.04, 24.04 | Compatible, not recommended in this manual |
| 12.6 | 560.x | 20.04, 22.04, 24.04 | Legacy |

**Note:** This manual pins CUDA 13.0 with the 580.x.x `.run` driver. Use other versions only if your hardware or software requires it.

## How to Verify Compatibility Online
1. **For Drivers:** Go to [NVIDIA Drivers](https://www.nvidia.com/drivers/), select GPU and OS.
2. **For CUDA:** Go to [CUDA Downloads](https://developer.nvidia.com/cuda-downloads), choose OS and GPU. Always pick the `deb (local)` installer.

## Compatibility Troubleshooting
- **Driver too old for CUDA:** Install a newer NVIDIA driver by following section 4 with the `.run` file.
- **CUDA doesn't recognize GPU:** Verify with `nvidia-smi`. If fails, reinstall drivers.
- **`apt` wants to install `nvidia-driver-*` while installing CUDA:** you are calling a meta-package (`cuda` or `cuda-drivers`). Use only `cuda-toolkit-XX-Y`.
- **Kernel mismatch:** do **not** update the kernel to fix this. On 24.04 the kernel is pinned to the GA 6.8 track because of MongoDB ([Section 14](14-runbook-mongodb8-kernel.md)), and today an unpinned `apt upgrade` pulls 7.0 via HWE. Install the headers for the kernel you are already running (`sudo apt install linux-headers-$(uname -r)`) and reinstall the `.run`. See [Annex C](18-annex-c-kernel-matrix.md#annex-c-kernel-compatibility-matrix-ubuntu-2404-lts).
- **GCC incompatible:** Install correct version: `sudo apt install gcc-12 g++-12` and reconfigure with `update-alternatives` if needed.

## General Tips
- **Install in order:** `.run` driver (section 4) → CUDA Toolkit `.deb local` (section 5).
- **Test with samples:** clone [https://github.com/NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples) and build `deviceQuery` to validate GPU + toolkit.
- **If using Docker:** install `nvidia-container-toolkit` (not the deprecated `nvidia-docker2`) and run with `docker run --gpus all`.
- **Backup before changes:** Create snapshot or backup of drivers.

> **Additional Resources:**
> * [NVIDIA CUDA Toolkit Release Notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)
> * [NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
> * [Ubuntu NVIDIA Drivers PPA](https://launchpad.net/~graphics-drivers/+archive/ubuntu/ppa)

---

> [Index](../../README_en.md#index) · [Previous: Annex A: Identifying NVIDIA GPUs](16-annex-a-nvidia-gpus.md) · [Next: Annex C: Kernel Compatibility Matrix (Ubuntu 24.04 LTS)](18-annex-c-kernel-matrix.md) · [Español](../17-anexo-b-compatibilidad.md)
