# 3. Initial Ubuntu System Preparation

> [Index](../../README_en.md#index) · [Previous: 2. Ubuntu System Installation](02-ubuntu-installation.md) · [Next: 4. Installing NVIDIA Drivers on Ubuntu](04-nvidia-drivers.md) · [Español](../03-preparacion-del-sistema.md)

This section prepares Ubuntu to install the official NVIDIA driver with a `.run` file, which is the main path in this manual. Do not install the NVIDIA driver or CUDA yet; that comes in the next sections.

## Rule for this section

- We install updates, build tools, kernel headers, and base utilities.
- We set the graphical environment to Xorg to avoid NVIDIA conflicts.
- We can install **Ethernet/Wi-Fi** firmware or drivers if networking does not work.
- We do not use `ubuntu-drivers`, "Additional Drivers", or APT repositories to install NVIDIA.
- We do not run any `.run` installer yet.

## Step 1: Open a terminal

Press `Ctrl+Alt+T`.

If the machine asks for a password when using `sudo`, type your user password. The terminal will not show characters while you type; that is normal.

## Step 2: Check internet and network drivers

Before updating Ubuntu, confirm the machine has networking:

```bash
nmcli device status
ping -c 4 archive.ubuntu.com
```

Expected result:

- `nmcli` shows at least one connected interface.
- `ping` receives replies.

If **Ethernet or Wi-Fi does not appear**, identify the hardware:

```bash
lspci -nn | grep -Ei 'ethernet|network|wireless|wifi'
lsusb
```

Use that output to decide:

| Case | What to do |
|------|------------|
| Ethernet works, Wi-Fi does not | Connect an Ethernet cable and continue with the guide. Wi-Fi can be fixed later. |
| Wi-Fi works, Ethernet does not | Connect through Wi-Fi and continue with the guide. Ethernet can be fixed later. |
| Neither Ethernet nor Wi-Fi works | Use temporary internet through USB tethering from a phone or a Linux-compatible USB Ethernet/Wi-Fi adapter. |
| Broadcom Wi-Fi appears | With temporary internet, install `bcmwl-kernel-source`. |
| Intel/Realtek Wi-Fi appears but does not connect | With temporary internet, install or update `linux-firmware`. |
| Realtek RTL8125 Ethernet appears | If networking does not come up, review section 9 after getting temporary internet. |

With temporary internet, install base network firmware:

```bash
sudo apt update
sudo apt install -y linux-firmware
sudo reboot
```

> **Important:** It is allowed to use "Additional Drivers" for network drivers such as Broadcom Wi-Fi. Do not select NVIDIA drivers there; NVIDIA will be installed in section 4 with `.run`.

## Step 3: Update Ubuntu and reboot

First update the full system:

```bash
sudo apt update
sudo apt upgrade -y
```

When it finishes, reboot:

```bash
sudo reboot
```

After the reboot, open the terminal again.

## Step 4: Install tools required for `.run`

The NVIDIA `.run` installer needs to compile kernel modules. For that, it requires headers, DKMS, and build tools.

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) linux-headers-generic pkg-config gcc g++ make
sudo apt install -y libglvnd-dev libgl1-mesa-dev libegl1-mesa-dev libgles2-mesa-dev libx11-dev libxmu-dev libxi-dev libglu1-mesa-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y ca-certificates curl wget git vim nano mesa-utils inxi net-tools openssh-server ufw dnsutils htop ncdu tree traceroute nmap lm-sensors neofetch
```

## Step 5: Disable Wayland and use Xorg

For this manual, we use Xorg because it is usually more predictable with NVIDIA drivers installed through `.run`.

Edit the GDM3 configuration:

```bash
sudo nano /etc/gdm3/custom.conf
```

Find this line:

```ini
#WaylandEnable=false
```

Leave it like this, without `#` at the beginning:

```ini
WaylandEnable=false
```

Save with `Ctrl+O`, press `Enter`, and exit with `Ctrl+X`.

Reboot to apply the change:

```bash
sudo reboot
```

## Step 6: Prepare remote access if you will use it

If the machine will be managed from another computer, enable SSH and allow it through the firewall:

```bash
sudo systemctl enable --now ssh
sudo ufw allow ssh
sudo ufw --force enable
```

If you will not use remote access, you can skip this step.

> **An active firewall with half the rules in place breaks services.** Here UFW comes up
> with SSH only, which is correct at this point because nothing else is installed yet.
> The stack ports (MongoDB, MQTT, EMQX dashboard, RTSP, Node-RED, AnyDesk) are added in
> Sections 6 and 7. If this machine will run those services, **do not leave it like
> this**: with UFW active and a port not allowed, the service starts fine and is still
> unreachable from the network, and troubleshooting goes to the service instead of the
> firewall. Check what is allowed with `sudo ufw show added` (it works even with the
> firewall off; `sudo ufw status` lists nothing while inactive).

## Step 7: Apply adjustments for your Ubuntu version

First check your version:

```bash
lsb_release -rs
```

> **On Linux Mint** this command returns Mint's version (for example `22.1`), not Ubuntu's.
> The base is what counts: read it from `/etc/upstream-release/lsb-release` and apply the
> adjustments for that version.

For **Ubuntu 22.04 LTS**, install GCC/G++ 12 if you will use CUDA versions that require it:

```bash
sudo apt install -y gcc-12 g++-12
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 120
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-12 120
```

For **Ubuntu 24.04 LTS**, install `libtinfo5` only if CUDA or an older tool requests it:

```bash
wget http://security.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2ubuntu0.3_amd64.deb
sudo apt install ./libtinfo5_6.3-2ubuntu0.3_amd64.deb
rm libtinfo5_6.3-2ubuntu0.3_amd64.deb
```

If `wget` returns 404, Ubuntu published a newer patch and removed the old one: take the highest `libtinfo5_6.3-2ubuntu0.*_amd64.deb` from http://security.ubuntu.com/ubuntu/pool/universe/n/ncurses/ (the doctor with `--fix` already resolves it on its own).

If you do not know whether you need it, you can leave it for later. It does not block NVIDIA driver installation.

For **Ubuntu 24.04 LTS on machines that will run MongoDB 8** (every compression and analytics
workstation), pin the kernel to the **GA 6.8** track before installing any other package. MongoDB 8
refuses to start on kernels 6.19 – 7.0.13, which is what the HWE stack on 24.04.4+ ISOs installs:

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

sudo apt-mark hold linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 \
                    linux-headers-generic-hwe-24.04
sudo apt update
sudo apt install --install-recommends linux-generic
```

Verify the pin hit the right target and did **not** drag the GA track down with it:

```bash
uname -r                                   # 6.8.0-1XX-generic if you are already on GA
apt-cache policy linux-generic-hwe-24.04   # expected: Candidate: (none), priority -1
apt-cache policy linux-image-generic       # expected: 500 / 6.8.0-1XX.XXX  <- must NOT be -1
```

> **If `uname -r` already shows `7.0.0-XX`**, the machine was born with HWE installed and this
> pinning only stops it from getting worse: the 7.0 still has to be purged. Do not continue with
> MongoDB; go to [Section 14, Case A](14-runbook-mongodb8-kernel.md#case-a--machine-already-deployed-running-kernel-70).

> **If `uname -r` shows 6.9 – 6.18, do not take it down to 6.8.** MongoDB 8's ceiling is 6.19:
> every kernel below that starts `mongod` fine. The `6.11` from a 24.04.2 ISO, the `6.14` from a
> 24.04.3 and the `6.14` that ships with Linux Mint 22.2 are already compatible, and downgrading
> them to 6.8 gives up hardware support without fixing anything. Apply the pinning anyway: noble's
> HWE points at 7.0 today, so without the pin the next `apt full-upgrade` does break MongoDB. And
> when you purge the HWE metapackages, mark the running kernel manual so no `autoremove` takes it:
>
> ```bash
> sudo apt-mark manual linux-image-$(uname -r) linux-modules-$(uname -r) \
>                      linux-modules-extra-$(uname -r) linux-headers-$(uname -r)
> ```
>
> GA 6.8 stays installed as the managed track (it keeps getting patches and is the fallback to
> boot), and the machine keeps running the kernel it already had. The tradeoff to know: that
> kernel freezes at its current ABI, because the metapackage that moved it forward is exactly the
> one being blocked.

## Step 8: Verify the preparation is ready

Run:

```bash
gcc --version
dkms status
ls /usr/src/linux-headers-$(uname -r)
echo $XDG_SESSION_TYPE
```

Expected result:

- `gcc --version` shows an installed version.
- `dkms status` does not show an error, although it may not list anything yet.
- `ls /usr/src/linux-headers-$(uname -r)` shows kernel files.
- `echo $XDG_SESSION_TYPE` should show `x11` if you are in a graphical session.

## If something fails during preparation

| Problem | What to try first |
|---------|-------------------|
| `apt update` fails | Check internet with `ping -c 4 archive.ubuntu.com`. |
| Wi-Fi does not appear | Use Ethernet or temporary USB tethering and install `linux-firmware`; if it is Broadcom, install `bcmwl-kernel-source`. |
| Ethernet does not appear | Use Wi-Fi, USB tethering, or a temporary USB adapter; then check the chip with `lspci -nn`. |
| Packages do not install | Run `sudo apt --fix-broken install` and repeat the command. |
| Kernel headers are missing | Run `sudo apt install -y linux-headers-$(uname -r) linux-headers-generic`. |
| `echo $XDG_SESSION_TYPE` shows `wayland` | Check `/etc/gdm3/custom.conf`, confirm `WaylandEnable=false`, and reboot. |
| SSH does not connect | Check the machine IP with `ip a` and firewall status with `sudo ufw status`. |
| You do not know whether an NVIDIA driver is already installed | Do not install over it. [Section 4](04-nvidia-drivers.md) will clean up before the `.run`. |

---

> [Index](../../README_en.md#index) · [Previous: 2. Ubuntu System Installation](02-ubuntu-installation.md) · [Next: 4. Installing NVIDIA Drivers on Ubuntu](04-nvidia-drivers.md) · [Español](../03-preparacion-del-sistema.md)
