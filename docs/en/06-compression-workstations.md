# 6. Specific Setup for Compression Workstations

> [Index](../../README_en.md#index) · [Previous: 5. Installing CUDA Toolkit](05-cuda-toolkit.md) · [Next: 7. Specific Setup for Analytics Workstations](07-analytics-workstations.md) · [Español](../06-estaciones-compresion.md)

> **Note:** This section installs tools for compression/data workstations, assuming Ubuntu 24.04.1 LTS with CUDA/drivers installed. Tools are optional; install only what's necessary. Check versions on official sites.

## Installing MongoDB (NoSQL Database)

### Step 0: Verify the kernel is compatible

MongoDB 8 **will not start** on Linux kernels 6.19 – 7.0.13 (TCMalloc/rseq bug,
[SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). Before installing:

```bash
uname -r                        # expected: 6.8.0-1XX-generic
cat /proc/version_signature     # real upstream base, e.g. "... 6.8.0-136.136"
```

- If you see `6.8.0-1XX-generic`, continue with Step 1. If you have not applied the preventive
  pinning from [Section 3, Step 7](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version), do it now —
  without it, a future `apt upgrade` reinstalls HWE and leaves the machine without a database.
- If you see `7.0.0-XX-generic`, **do not install MongoDB yet**: go to
  [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70) and come back here when done.

### Step 1: Add Repository
Import GPG key:
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
```

Add repository (adjust `jammy` to `noble` if using Ubuntu 24.04):
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

### Step 2: Install MongoDB
```bash
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### Step 3: Start and Enable Service
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Verification:**
```bash
sudo systemctl status mongod
mongosh --eval "db.runCommand('ping')"
# Should show "ok": 1
```

> **Note on Transparent Huge Pages:** MongoDB 8.0 requires THP **enabled**, the opposite of 7.0 and
> earlier. If an old provisioning script left `transparent_hugepage=never` in `GRUB_CMDLINE_LINUX`
> or a systemd unit that disables it, remove it. Check with
> `cat /sys/kernel/mm/transparent_hugepage/enabled` (should show `[always]` or `[madvise]`).

## Installing MongoDB Compass (GUI for MongoDB)

### Step 1: Download and Install
Download from [https://www.mongodb.com/try/download/compass](https://www.mongodb.com/try/download/compass):
```bash
wget https://downloads.mongodb.com/compass/mongodb-compass_1.49.15_amd64.deb
sudo apt install -y ./mongodb-compass_1.49.15_amd64.deb
```

If dependencies missing:
```bash
sudo apt --fix-broken install
```

### Step 2: Run Compass
```bash
mongodb-compass &
```

**Verification:** Open the app and connect to `mongodb://localhost:27017`.

**Uninstallation (optional):**
```bash
sudo apt remove -y mongodb-compass
```

## Installing EMQX (MQTT Broker)

### Step 1: Install from Repository
```bash
curl -sL https://assets.emqx.com/scripts/install-emqx-deb.sh | sudo bash
sudo apt-get install -y emqx
```

### Step 2: Start and Enable
```bash
sudo systemctl start emqx
sudo systemctl enable emqx
```

**Verification:**
```bash
sudo systemctl status emqx
# Dashboard at http://localhost:18083 (EMQX initial credentials: admin / public; change them on first login)
```

> **If `emqx` installs but the service never starts:** EMQX 5 will not start without
> `/etc/emqx/acl.conf`. That file is a dpkg *conffile*, and dpkg treats its absence as
> an admin decision: if someone deleted or moved it, neither the install nor a plain
> `--reinstall` puts it back. `--force-confmiss` is the only way to restore it from the
> package:
>
> ```bash
> ls -l /etc/emqx/acl.conf     # if it is missing, this is your problem
> sudo apt-get install -y --reinstall -o Dpkg::Options::=--force-confmiss emqx
> sudo systemctl start emqx && systemctl is-active emqx
> ```

## Installing Golang

### Step 1: Install with Snap
```bash
sudo snap install go --classic
```

**Verification:**
```bash
go version
# Should show installed version
```

## Installing Visual Studio Code

### Step 1: Install with Snap
```bash
sudo snap install code --classic
```

**Verification:**
```bash
code --version
# Should show version
```

## Installing GStreamer and Plugins

### Step 1: Install Plugins
```bash
sudo apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio gstreamer1.0-rtsp
```

**Verification:**
```bash
gst-inspect-1.0 rtspclientsink
gst-inspect-1.0 nvh264enc
# Should show plugin info
```

## Installing Angry IP Scanner

### Step 1: Download and Install
Download from [https://github.com/angryip/ipscan/releases](https://github.com/angryip/ipscan/releases):
```bash
wget https://github.com/angryip/ipscan/releases/download/3.9.1/ipscan_3.9.1_amd64.deb
sudo apt install -y ./ipscan_3.9.1_amd64.deb
```

**Verification:** Run `ipscan` from terminal or menu.

## Installing AnyDesk (Remote Support)

### Step 1: Add Repository and Install
```bash
sudo apt update
sudo apt install -y ca-certificates curl apt-transport-https
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://keys.anydesk.com/repos/DEB-GPG-KEY -o /etc/apt/keyrings/keys.anydesk.com.asc
sudo chmod a+r /etc/apt/keyrings/keys.anydesk.com.asc
echo "deb [signed-by=/etc/apt/keyrings/keys.anydesk.com.asc] https://deb.anydesk.com all main" | sudo tee /etc/apt/sources.list.d/anydesk-stable.list > /dev/null
sudo apt update
sudo apt install -y anydesk
```

### Step 2: Configure the service for NVIDIA and X11 compatibility

> **Important:** On machines with the NVIDIA driver installed via `.run` and Xorg forced, the AnyDesk service starts as `root` without access to the user's X11 display. Without this fix, AnyDesk crashes at startup and creates a CPU loop that freezes the GNOME desktop. This step is mandatory on compression workstations.

Create the service override:

```bash
sudo mkdir -p /etc/systemd/system/anydesk.service.d
sudo tee /etc/systemd/system/anydesk.service.d/override.conf > /dev/null << 'EOF'
[Service]
Environment=DISPLAY=:0
Environment=XAUTHORITY=/run/user/1000/gdm/Xauthority
Environment=LIBGL_ALWAYS_SOFTWARE=1
ExecStartPre=/bin/sleep 5
EOF
```

Apply the changes:

```bash
sudo systemctl daemon-reload
sudo systemctl enable anydesk
sudo systemctl start anydesk
```

**Verification (optional):**
```bash
sudo systemctl status anydesk
# Should show "active (running)" without errors
sudo systemctl cat anydesk | grep -A6 "override.conf"
# Should show the 4 lines of the override
```

### Step 3: Configure Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 6568/tcp
sudo ufw allow 50001:50003/udp
```

**Verification:** Run `anydesk` and note the ID.

## Installing RustDesk (Remote Support Alternative)

### Step 1: Download and Install
Download from [https://github.com/rustdesk/rustdesk/releases](https://github.com/rustdesk/rustdesk/releases):
```bash
wget https://github.com/rustdesk/rustdesk/releases/download/1.2.3/rustdesk-1.2.3-x86_64.deb
sudo apt install -y ./rustdesk-1.2.3-x86_64.deb
```

**Verification:** Run `rustdesk` and configure ID/password.

## Configuring Ports for Compression Workstations (Optional)
If you enabled UFW in section 3, open necessary ports for apps to function correctly. If not using firewall, skip this section.

| Application | Ports | Protocol | Command to Open (Optional) |
|------------|---------|-----------|-------------------------------|
| MongoDB | 27017 | TCP | `sudo ufw allow 27017/tcp` |
| EMQX MQTT | 1883 | TCP | `sudo ufw allow 1883/tcp` |
| EMQX Dashboard | 18083 | TCP | `sudo ufw allow 18083/tcp` |
| GStreamer RTSP | 554 | TCP/UDP | `sudo ufw allow 554/tcp && sudo ufw allow 554/udp` |
| AnyDesk | 80, 443, 6568 | TCP | `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 6568/tcp` |
| AnyDesk (UDP) | 50001-50003 | UDP | `sudo ufw allow 50001:50003/udp` |
| RustDesk | Dynamic (check logs) | TCP/UDP | Configure as needed |
| SSH (if using) | 22 (or custom) | TCP | `sudo ufw allow ssh` |

**General verification (optional):**
```bash
sudo ufw status
netstat -tlnp | grep LISTEN  # Lists open ports
```

**Tips (optional):**
- For remote access, open only necessary ports and from specific IPs: `sudo ufw allow from <IP> to any port 27017`.
- If using VPN, adjust rules.
- Check app logs for additional ports (e.g., `sudo journalctl -u emqx`).

## General Tips
- Check services: `sudo systemctl status <service>`.
- Configure unique passwords for remote access.
- Review plugins: Use `gst-inspect-1.0` for GStreamer.

## Troubleshooting
- **MongoDB not starting:** Check logs: `sudo journalctl -u mongod`.
- **MongoDB not starting and the journal says `MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility`:** The machine is running the HWE 7.0 kernel. Confirm with `uname -r` and apply [Section 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-fails-to-start-on-hwe-kernel-70). Reinstalling `mongodb-org` or editing `/etc/mongod.conf` will not help.
- **EMQX failing:** Verify ports: `netstat -tlnp | grep 1883`.
- **EMQX installed but the service is dead and `/etc/emqx/acl.conf` is missing:** dpkg does not restore a conffile that was deleted or moved. Run `sudo apt-get install -y --reinstall -o Dpkg::Options::=--force-confmiss emqx`, then `sudo systemctl start emqx`. `workstation-doctor-compresion` detects and fixes this case.
- **GStreamer plugins missing:** `sudo apt install gstreamer1.0-plugins-*`.
- **AnyDesk/RustDesk not connecting:** Temporarily disable firewall for testing.
- **AnyDesk freezes the desktop on startup (gnome-shell at 70–100% CPU):** The AnyDesk service has no access to the X11 display. Check that the Step 2 override is applied with `sudo systemctl cat anydesk`. If the `override.conf` block does not appear, repeat Step 2 and run `sudo systemctl daemon-reload && sudo systemctl restart anydesk`. Additional symptom: `_usr_bin_anydesk.1000.crash` shows up in `/var/crash/`.
- **AnyDesk shows "Authorization required, but no authorization protocol specified":** The service starts before X11 is ready or without the `DISPLAY`/`XAUTHORITY` variables. The `ExecStartPre=/bin/sleep 5` in the override fixes the timing; check that it is present.

> **Additional Resources:**
> * [MongoDB Docs](https://www.mongodb.com/docs/)
> * [EMQX Docs](https://www.emqx.io/docs/)
> * [GStreamer Docs](https://gstreamer.freedesktop.org/documentation/)

---

> [Index](../../README_en.md#index) · [Previous: 5. Installing CUDA Toolkit](05-cuda-toolkit.md) · [Next: 7. Specific Setup for Analytics Workstations](07-analytics-workstations.md) · [Español](../06-estaciones-compresion.md)
