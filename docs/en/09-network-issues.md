# 9. Common Network Issues with New Motherboards

> [Index](../../README_en.md#index) · [Previous: 8. Managing the Graphical Interface](08-graphical-interface.md) · [Next: 10. Wake-on-LAN (WOL): Windows to Windows and Ubuntu to Windows](10-wake-on-lan.md) · [Español](../09-redes-placas-nuevas.md)

> **Note:** Network problems with new motherboards are usually due to incompatible drivers. Use `lspci | grep Network` to identify the chip. Restart after changes.

> **⚠️ Before installing the HWE kernel to fix a NIC:** on any station running MongoDB 8 — that is,
> every compression and analytics station — that path is **closed**. The 24.04 HWE kernel pulls in
> the 7.0 series, which prevents `mongod` from starting
> ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)), and the pin from
> [Section 3 Step 7](03-system-preparation.md#step-7-apply-adjustments-for-your-ubuntu-version) leaves it with no candidate:
> the `apt install` will fail with `has no installation candidate`.
>
> What you need is a newer **driver**, not a newer kernel. The full procedure, in the order that
> keeps you from losing network halfway through, is in
> [Case C of Section 14](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel).

## Problems with Realtek RTL8125 (Ethernet)

### Diagnosis
```bash
ip link show  # Look for ethX/enpXsY DOWN
lspci | grep RTL8125  # Confirm chip
```

### Fix

Check the chip revision first, because it decides everything else:

```bash
lspci -nn | grep -i 8125             # confirm the PCI ID (10ec:8125)
dmesg | grep -iE 'r8169|r8125|XID'   # the revision shows up as "XID <n>"
```

| Revision | XID | What handles it |
|---|---|---|
| RTL8125A / B / C | 605, 641, 648… | The GA 6.8 in-tree `r8169`, unaided. Change nothing |
| **RTL8125D** | **688** | Neither the GA `r8169` nor Ubuntu's `r8125-dkms`. See below |

> **An active `r8169` is not, on its own, a problem.** It is the correct driver for the A/B/C
> revisions on any kernel, and for **all** of them —rev D included— on the HWE 7.x kernels, where
> the support is already in-tree. The only case where `r8169` is the wrong driver is **RTL8125D
> (XID 688) on the GA 6.8 track**. Concluding "r8125 must be installed" from seeing `r8169` alone is
> the classic false positive of this section.

If the interface is UP and `basename $(readlink -f /sys/class/net/<iface>/device/driver)` says
`r8169`, it already works: install nothing.

For A/B/C revisions that do not come up, the package from Ubuntu's repos is enough:

```bash
sudo apt update
sudo apt install -y dkms build-essential linux-headers-generic
sudo apt install -y r8125-dkms        # for RTL8168/8111 use r8168-dkms
```

> **Before installing `r8125-dkms` on a machine you are about to move down to GA:** that package
> (9.011.00) drops an `r8125.ko` under `updates/dkms/` that does **not** support the RTL8125D, and
> with it the pre-reboot check of [Case C](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel)
> goes green on a board that will still come up with no network. If the board is rev D, or you
> cannot determine the revision, skip this route: go straight to the vendor driver (>= 9.014.01) or
> to `sudo nic-driver-rescue`.

> **For the RTL8125D (XID 688) that package does not work.** noble ships `r8125-dkms` 9.011.00,
> whose detection code only covers up to revision C and sends XID 688 to `unknown chip version`.
> You need the vendor driver, version **9.014.01 or newer**. The full procedure — in the order that
> keeps you from losing the network halfway through — is in
> [Case C of Section 14](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel).

> **Do not blacklist `r8169`.** It is a common reflex and here it does damage: RTL8168/8111 NICs
> (`10ec:8168`) depend on it, and on dual-port boards it is often the only working link. It is also
> unnecessary: both modules declare the `10ec:8125` alias, so `modprobe` loads both and the device
> goes to **whichever probes successfully first**. `r8169` ships in the initramfs and gets there
> earlier, so it keeps the revisions it supports and `r8125` stays loaded but unused; on the
> revisions it does not support it fails the probe, releases the device, and `r8125` takes it.

Being DKMS, the module is rebuilt on every kernel change, so this path is compatible with the GA
track pin that MongoDB 8 requires.

**Verification (optional):** `ip link show` (should be UP), `lspci | grep -i ethernet`

## Problems with Intel Ethernet (e.g., I219, I225, I226)

### Diagnosis
```bash
lspci | grep -i ethernet              # Look for Intel controller
dmesg | grep -Ei 'e1000e|igc|igb'     # Driver errors
ip link show                          # UP/DOWN state of the interface
```

Intel I219 chips use the `e1000e` driver, while I225/I226 use `igc`. Both ship with the Ubuntu kernel; the issue is almost always an outdated kernel or missing firmware.

### Solution

1. Update the system and firmware:
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y linux-firmware
   ```
2. Check whether the driver in the kernel you intend to run knows your board. Take the PCI ID from
   `lspci -nn` — for example `8086:125c` — and ask the module:
   ```bash
   lspci -nn | grep -Ei 'ethernet'
   modinfo igc | grep -i 'pci:v00008086d0000125C'   # adjust the ID to your board
   ```
   If the alias shows up, the driver supports the chip and the problem is elsewhere: firmware, BIOS,
   or point 4.
3. If the alias does **not** show up, that kernel's driver is too old for the board.

   > **Do not install `linux-generic-hwe-24.04` if the station runs MongoDB 8.** That is the 7.0
   > series kernel that prevents `mongod` from starting. Follow
   > [Case C of Section 14](14-runbook-mongodb8-kernel.md#case-c--boards-whose-nic-does-not-work-on-the-ga-kernel), which fixes the
   > NIC without switching kernel tracks.

   On a machine that will **not** run MongoDB, HWE is still valid:
   ```bash
   sudo apt install -y --install-recommends linux-generic-hwe-24.04
   ```
   For Ubuntu 22.04 use `linux-generic-hwe-22.04`.
4. If the chip comes up but the link is unstable and `dmesg` shows `igc` errors, try disabling
   TSO/GSO temporarily:
   ```bash
   sudo ethtool -K enpXsY tso off gso off gro off
   ```

**Verification:** `ip a` (IP assigned), `ping 8.8.8.8`

> **Note:** The `backport-iwlwifi-dkms` package is for Intel **Wi-Fi** cards (`iwlwifi` chipset), not for Ethernet. Do not install it to fix I219/I225/I226 issues.

## Problems with Wi-Fi (Broadcom, etc.)

### Diagnosis
```bash
iwconfig  # List Wi-Fi interfaces
lspci | grep Network  # Identify chip
```

### Solution for Broadcom
1. Install bcmwl: `sudo apt install bcmwl-kernel-source`
2. Restart: `sudo reboot`

**Verification:** `iwconfig` (should show wlan0 UP)

## DNS Not Resolving Names

### Diagnosis
```bash
nslookup google.com  # Failing?
cat /etc/resolv.conf  # Nameservers
```

### Solution
1. Edit resolv.conf: `sudo nano /etc/resolv.conf`
2. Add: `nameserver 8.8.8.8` and `nameserver 1.1.1.1`
3. Or use systemd: `sudo systemctl restart systemd-resolved`

**Verification:** `nslookup google.com` (should resolve)

## Slow or Intermittent Connection

### Diagnosis
```bash
speedtest-cli  # Speed
dmesg | grep -i network  # Errors
```

### Solution
1. Disable IPv6: `sudo nano /etc/sysctl.conf` add `net.ipv6.conf.all.disable_ipv6=1`
2. Apply: `sudo sysctl -p`
3. Change MTU: `sudo ip link set dev enpXsY mtu 1450`

**Verification:** `speedtest-cli`, restart and test.

## Configure Static IP

### Solution
1. Edit Netplan: `sudo nano /etc/netplan/01-netcfg.yaml`
2. Example (documentation addresses; use your own network's):
   ```yaml
   network:
     version: 2
     ethernets:
       enp0s3:
         dhcp4: no
         addresses: [192.0.2.10/24]
         routes:
           - to: default
             via: 192.0.2.1
         nameservers:
           addresses: [8.8.8.8, 1.1.1.1]
   ```
   > **Note:** `gateway4` has been deprecated since Netplan 0.105+. Use `routes` as shown above.
3. Apply: `sudo netplan apply`

**Verification:** `ip a` (static IP), `ping google.com`

## Problems with VPN

### Diagnosis
```bash
sudo systemctl status openvpn  # If using OpenVPN
journalctl -u openvpn  # Logs
```

### Solution
1. Install OpenVPN: `sudo apt install openvpn`
2. Connect: `sudo openvpn config.ovpn`
3. For WireGuard: `sudo apt install wireguard` and configure.

**Verification:** `ip a` (tun interface), `curl ifconfig.me` (external IP changes)

## General Troubleshooting
- **Not connecting:** `sudo systemctl restart NetworkManager`
- **Missing drivers:** Search in repos: `sudo apt search <chip>`
- **Logs:** `sudo journalctl -u NetworkManager`
- **Reset:** `sudo nmcli networking off && sudo nmcli networking on`

> **Tip:** If nothing works, install drivers from manufacturer's site or use USB Ethernet.

---

> [Index](../../README_en.md#index) · [Previous: 8. Managing the Graphical Interface](08-graphical-interface.md) · [Next: 10. Wake-on-LAN (WOL): Windows to Windows and Ubuntu to Windows](10-wake-on-lan.md) · [Español](../09-redes-placas-nuevas.md)
