# 11. Post-Installation Script (Optional)

> [Index](../../README_en.md#index) · [Previous: 10. Wake-on-LAN (WOL): Windows to Windows and Ubuntu to Windows](10-wake-on-lan.md) · [Next: 12. Doctor Verification Scripts](12-doctor-scripts.md) · [Español](../11-script-post-instalacion.md)

> **Note:** This script automates initial preparation (section 3). Update as needed. Run as root or with sudo.

## Improved `setup.sh` Script
Includes additional dependencies and options.

```bash
#!/bin/bash
# Script for initial Ubuntu system preparation
# Improved version with more tools

set -e  # Exit on error

echo "--- Updating system ---"
sudo apt update && sudo apt upgrade -y

echo "--- Installing common dependencies ---"
sudo apt install -y build-essential dkms pkg-config libglvnd-dev libgl1-mesa-dev libegl1-mesa-dev libgles2-mesa-dev libx11-dev libxmu-dev libxi-dev libglu1-mesa-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev mesa-utils inxi net-tools openssh-server curl git wget htop ncdu tree traceroute nmap vim lm-sensors neofetch

echo "--- Configuring GDM3 (disable Wayland) ---"
sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf

echo "--- Configuring firewall (optional) ---"
read -p "Enable UFW with SSH? (y/n): " ufw_choice
if [[ $ufw_choice =~ ^[yY]$ ]]; then
  sudo ufw allow ssh
  sudo ufw --force enable
fi

echo "--- Verifications ---"
echo "GCC version: $(gcc --version | head -1)"
echo "Git version: $(git --version)"
echo "Firewall status: $(sudo ufw status | head -1)"

echo "--- Preparation completed. Restart recommended. ---"
read -p "Restart now? (y/n): " choice
case "$choice" in
  y|Y ) sudo reboot;;
  * ) echo "Run 'sudo reboot' manually.";;
esac
```

## How to Use It
1. Create file: `nano setup.sh`
2. Paste content and save.
3. Permissions: `chmod +x setup.sh`
4. Run: `./setup.sh` (or `sudo ./setup.sh` if needs root)

## Customization
- Add more installs: `sudo apt install -y <package>`
- Remove options: Comment lines with `#`
- Logging: Add `>> setup.log` to commands.

## Troubleshooting
- If fails: Check logs in terminal.
- Permissions: Ensure script has execution.
- Dependencies: Verify internet for apt.

---

> [Index](../../README_en.md#index) · [Previous: 10. Wake-on-LAN (WOL): Windows to Windows and Ubuntu to Windows](10-wake-on-lan.md) · [Next: 12. Doctor Verification Scripts](12-doctor-scripts.md) · [Español](../11-script-post-instalacion.md)
