# FAQ: Frequently Asked Questions

> [Index](../../README_en.md#index) · [Previous: 14. Runbook: MongoDB 8 Fails to Start on HWE Kernel 7.0](14-runbook-mongodb8-kernel.md) · [Next: Annex A: Identifying NVIDIA GPUs](16-annex-a-nvidia-gpus.md) · [Español](../15-faq.md)

* **What if NVIDIA driver doesn't install correctly?**
  * Check compatibility in Annex B and ensure old drivers are removed. Run `sudo apt purge nvidia*` and restart before reinstalling.

* **How do I know which CUDA version to install?**
  * Check the official website and verify compatibility with your GPU. For this manual, keep the driver on the 580.x.x branch and choose a CUDA version compatible with that branch.

* **Why doesn't Wake-on-LAN work?**
  * Check BIOS settings, power options, and ensure PC is connected by cable. Run `sudo ethtool enpXsY` to check WOL support.

* **Can I use this guide on Ubuntu variants?**
  * Yes, but minor differences may occur. Ubuntu Desktop is recommended. For Server, omit GUI sections.

* **How do I verify my GPU is compatible?**
  * Use `lspci -nn | grep VGA` for Device ID, then search in Annex A. Confirm with `nvidia-smi` after installing drivers.

* **What if CUDA doesn't recognize the GPU?**
  * Ensure drivers are installed correctly (`nvidia-smi`). Restart if necessary. Check compatibility in Annex B.

* **Why does screen go black after installing drivers?**
  * Add `nomodeset` in GRUB (section 2). If using GDM3, force Xorg in `/etc/gdm3/custom.conf`.

* **How do I configure network on new motherboards?**
  * Identify chip with `lspci | grep Network`, install appropriate drivers (e.g., `sudo apt install r8168-dkms` for Realtek).

* **Can I use Docker with NVIDIA GPUs?**
  * Yes, install `nvidia-container-toolkit` (replaces the deprecated `nvidia-docker2`). Follow the [official guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html), then `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`, and run containers with `docker run --gpus all`.

* **How do I free GPU memory for other apps?**
  * Disable graphical environment: `sudo systemctl set-default multi-user.target && sudo reboot`. Reactivate with `graphical.target`.

* **What if MongoDB or Node-RED don't start?**
  * Check logs: `sudo journalctl -u mongod` or `sudo journalctl -u nodered`. Verify ports with `sudo netstat -tlnp`.

* **`mongod` won't start and the log mentions "Linux kernel versions 6.19 and newer". What's going on?**
  * The machine is on the HWE 7.0 kernel and MongoDB 8 refuses to start in the 6.19 – 7.0.13 range ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). It is not a MongoDB config issue: you have to go back to the GA 6.8 track. Follow [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70).

* **How do I update kernel without breaking drivers?**
  * Update normally: `sudo apt update && sudo apt upgrade`. If issues, reinstall drivers after. **Exception:** on machines running MongoDB 8, do not install the HWE kernel (`linux-generic-hwe-24.04`); stay on the GA 6.8 track with the pinning from [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70). The GA track keeps receiving security patches until 24.04 end of life.

* **Why does `uname -r` show `7.0.0-XX` if Canonical already shipped the fixed kernel?**
  * Ubuntu keeps `X.Y.0-ABI` fixed in `uname -r` and only bumps the ABI number, even when it rebases the upstream sublevel internally. MongoDB's guard reads that string, so it keeps blocking even on an already-patched kernel. Check the real base with `cat /proc/version_signature`.

* **Is the post-install script safe?**
  * Review code before running. It makes backups and configures as per guide, but use cautiously in production.

* **Where do I find error logs?**
  * Drivers: `/var/log/nvidia-installer.log`. System: `sudo journalctl -xe`. CUDA: logs in `/var/log/cuda-installer.log`.

* **How do I uninstall everything NVIDIA to reinstall?**
  * Run `sudo apt purge nvidia* cuda*`, remove `/usr/local/cuda*`, restart and follow guide from start.

---

> [Index](../../README_en.md#index) · [Previous: 14. Runbook: MongoDB 8 Fails to Start on HWE Kernel 7.0](14-runbook-mongodb8-kernel.md) · [Next: Annex A: Identifying NVIDIA GPUs](16-annex-a-nvidia-gpus.md) · [Español](../15-faq.md)
