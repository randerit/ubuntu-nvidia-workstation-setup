# 10. Wake-on-LAN (WOL): Windows to Windows and Ubuntu to Windows

> [Index](../../README_en.md#index) · [Previous: 9. Common Network Issues with New Motherboards](09-network-issues.md) · [Next: 11. Post-Installation Script (Optional)](11-post-install-script.md) · [Español](../10-wake-on-lan.md)

> **Note:** WOL wakes PCs by network sending a "magic packet". Requires Ethernet (not Wi-Fi). Configure BIOS and OS first.

## Configure WOL on Target PC (Windows/Ubuntu)

### In BIOS/UEFI
1. Enter BIOS (F2/DEL).
2. Go to "Power Management" > "Wake on LAN" > "Enabled".
3. "AC Power Loss" > "Power On" (optional).
4. Save and exit.

### In Windows
1. Run `powercfg /devicequery wake_armed` (lists devices that can wake).
2. In Device Manager > Network Adapter > Properties > Power Management > Check "Allow this device to wake the computer".
3. In Power Options > "Allow wake timers".

### In Ubuntu
1. Install ethtool: `sudo apt install ethtool`
2. Enable WOL: `sudo ethtool -s enpXsY wol g` (replace enpXsY with interface, e.g., `ip link show`)
3. Verify: `sudo ethtool enpXsY | grep Wake-on`
4. For persistence: Create `/etc/systemd/system/wol.service` with:
   ```
   [Unit]
   Description=Enable WOL
   After=network.target

   [Service]
   Type=oneshot
   ExecStart=/usr/sbin/ethtool -s enpXsY wol g

   [Install]
   WantedBy=multi-user.target
   ```
   Enable: `sudo systemctl enable wol`

**Verification:** Turn off PC, wait 1 min, send packet from another device.

## Send WOL Packet from Windows (to Windows or Ubuntu)

### PowerShell Script
Save as `Send-WOL.ps1` and run: `.\Send-WOL.ps1 -Mac AA:BB:CC:DD:EE:FF`

Works for waking Windows or Ubuntu PCs configured for WOL.

```powershell
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)] [string]$Mac,
  [string]$Broadcast = "255.255.255.255",
  [int]$Port = 9
)

$macClean = ($Mac -replace '[:-]','')
if ($macClean.Length -ne 12) { throw "Invalid MAC: $Mac" }

$macBytes = 0..5 | ForEach-Object { [Convert]::ToByte($macClean.Substring($_*2,2),16) }

$packet = New-Object byte[] (6 + 16*6)
for ($i=0; $i -lt 6; $i++) { $packet[$i] = 0xFF }
for ($i=0; $i -lt 16; $i++) { [Array]::Copy($macBytes, 0, $packet, 6 + $i*6, 6) }

$udp = New-Object System.Net.Sockets.UdpClient
$udp.EnableBroadcast = $true
[void]$udp.Send($packet, $packet.Length, $Broadcast, $Port)
$udp.Close()
Write-Host "WOL sent to $Mac via $Broadcast:$Port"
```

## Send WOL Packet from Ubuntu

### Install tools
```bash
sudo apt install wakeonlan etherwake
```

### Send packet
```bash
wakeonlan -i 192.0.2.255 AA:BB:CC:DD:EE:FF  # Your network broadcast IP
# or
sudo etherwake -i enpXsY AA:BB:CC:DD:EE:FF
```

**Verification:** Use Wireshark/tcpdump to see packet: `sudo tcpdump -i enpXsY port 9`

## Troubleshooting
- **Not waking:** Check BIOS, power settings, firewall blocking port 9.
- **Wrong MAC:** `ip link show` or `arp -a` to get it.
- **Broadcast IP:** Use `ip route | grep default` for subnet.
- **Persistence:** In Ubuntu, add to cron: `@reboot sudo ethtool -s enpXsY wol g`

> **Note:** WOL by Wi-Fi doesn't work. Use Ethernet. Test with PCs on same local network.

---

> [Index](../../README_en.md#index) · [Previous: 9. Common Network Issues with New Motherboards](09-network-issues.md) · [Next: 11. Post-Installation Script (Optional)](11-post-install-script.md) · [Español](../10-wake-on-lan.md)
