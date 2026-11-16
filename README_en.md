# Ubuntu NVIDIA Workstation Setup

Guide and scripts to get an Ubuntu or Linux Mint workstation with an NVIDIA GPU up and running: installation, `.run` drivers, CUDA, workstation services, network diagnosis and recovery, Wake-on-LAN and basic hardening. Each chapter explains the reason behind every step and how to check that it worked.

[Español](README.md)

## What it covers

- **Systems:** Ubuntu 24.04 LTS as the reference, with notes for 22.04. Linux Mint 21.x (22.04 base) and 22.x (24.04 base). LMDE is not supported.
- **GPUs:** NVIDIA GeForce RTX 20, 30, 40 and 50 series, with the 580.x `.run` driver branch and CUDA 13.0.
- **Workstation profiles:** compression, analytics and visualization.

## Index

| Chapter | Contents |
|---------|----------|
| [Introduction](docs/en/00-introduction.md) | Overview of the whole process |
| [1. Requirements](docs/en/01-requirements.md) | What to prepare and Mint compatibility |
| [2. Ubuntu installation](docs/en/02-ubuntu-installation.md) | USB, BIOS/UEFI and installation |
| [3. System preparation](docs/en/03-system-preparation.md) | Updates, Xorg, remote access and per-version adjustments |
| [4. NVIDIA drivers](docs/en/04-nvidia-drivers.md) | `.run` installation, verification and removal |
| [5. CUDA Toolkit](docs/en/05-cuda-toolkit.md) | Local repository, toolkit and environment variables |
| [6. Compression workstations](docs/en/06-compression-workstations.md) | MongoDB, EMQX, GStreamer and remote support |
| [7. Analytics workstations](docs/en/07-analytics-workstations.md) | MongoDB with a user, Node-RED and Python for ML |
| [8. Graphical interface](docs/en/08-graphical-interface.md) | Enabling and disabling the desktop |
| [9. Network issues on new boards](docs/en/09-network-issues.md) | Realtek RTL8125, Intel, Wi-Fi, DNS and static IP |
| [10. Wake-on-LAN](docs/en/10-wake-on-lan.md) | Setup and sending the magic packet |
| [11. Post-installation script](docs/en/11-post-install-script.md) | Automated initial preparation |
| [12. Doctor scripts](docs/en/12-doctor-scripts.md) | Verification and installing what is missing |
| [13. Security](docs/en/13-security.md) | SSH, firewall, fail2ban and updates |
| [14. MongoDB 8 and kernel runbook](docs/en/14-runbook-mongodb8-kernel.md) | What to do if `mongod` will not start on HWE kernel 7.0 |
| [FAQ](docs/en/15-faq.md) | Frequently asked questions |
| [Annex A](docs/en/16-annex-a-nvidia-gpus.md) · [B](docs/en/17-annex-b-compatibility.md) · [C](docs/en/18-annex-c-kernel-matrix.md) | GPU identification, compatibility and kernel matrix |
| [Manual tests](docs/en/manual-tests.md) | How to verify the repository and a real machine |

## Quick start

1. Read the [requirements](docs/en/01-requirements.md) and follow chapters 2 to 5 in order.
2. Depending on the machine type, continue with chapter [6](docs/en/06-compression-workstations.md) or [7](docs/en/07-analytics-workstations.md).
3. Check the result with the doctor for the matching profile:

```bash
git clone https://github.com/randerit/ubuntu-nvidia-workstation-setup.git
cd ubuntu-nvidia-workstation-setup
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh      # or doctor_analitica.sh / doctor_visualizacion.sh
```

Without `--fix` the doctors only read. With `--fix` they install what is missing; use it on a test machine first.

## Scripts

All of them live in [`scripts/`](scripts/) and are run from the repository root. Libraries are looked up next to each script, so when copying them to another machine take the whole folder.

| Script | What it is for | Modifies the system |
|--------|----------------|---------------------|
| [`doctor_compresion.sh`](scripts/doctor_compresion.sh) | Verifies (and with `--fix` installs) what a compression workstation needs | Only with `--fix` |
| [`doctor_analitica.sh`](scripts/doctor_analitica.sh) | Same for an analytics workstation | Only with `--fix` |
| [`doctor_visualizacion.sh`](scripts/doctor_visualizacion.sh) | Same for a visualization workstation | Only with `--fix` |
| [`diag-nic.sh`](scripts/diag-nic.sh) | Layered diagnosis of one network port | No |
| [`fix-r8125-downgrade-6.8.sh`](scripts/fix-r8125-downgrade-6.8.sh) | Prepares the Realtek driver and the GA 6.8 kernel before rebooting (`--dry-run` to simulate) | Yes |
| [`doctor_lib.sh`](scripts/doctor_lib.sh), [`nic_lib.sh`](scripts/nic_lib.sh) | Shared libraries; not run directly | No |
| [`verificar_repo.sh`](scripts/verificar_repo.sh) | `shellcheck`, self-checks and documentation links | No |
| [`self_check_doctor_lib.sh`](scripts/self_check_doctor_lib.sh), [`self_check_nic_lib.sh`](scripts/self_check_nic_lib.sh) | Library tests against fake trees | No |
| [`check_links.py`](scripts/check_links.py) | Checks the relative links in the `.md` files | No |

Usage details and exit codes are in [chapter 12](docs/en/12-doctor-scripts.md).

## Structure

```text
.
├── README.md, README_en.md
├── docs/            Chapters in Spanish; docs/en/ holds the English version
├── scripts/         Doctors, network diagnosis, libraries and checks
└── LICENSE
```

## License

MIT. See [LICENSE](LICENSE).
