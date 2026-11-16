# 8. Managing the Graphical Interface

> [Index](../../README_en.md#index) · [Previous: 7. Specific Setup for Analytics Workstations](07-analytics-workstations.md) · [Next: 9. Common Network Issues with New Motherboards](09-network-issues.md) · [Español](../08-interfaz-grafica.md)

> **Note:** Ubuntu uses GDM3 as display manager. Manage graphical environment to free resources on servers or troubleshoot GPU issues.

## Check Current State
Before changing, check current target:
```bash
systemctl get-default  # Should show graphical.target or multi-user.target
who  # Shows active sessions
```

## Disable Graphical Environment (Text/Server Mode)
Useful for headless servers or troubleshooting.

### Step 1: Disable GDM3
```bash
sudo systemctl disable gdm3
sudo systemctl set-default multi-user.target
```

### Step 2: Restart
```bash
sudo reboot
```

**Verification:**
```bash
systemctl get-default  # multi-user.target
# You won't see graphical environment on boot
```

## Reactivate Graphical Environment
For normal desktop use.

### Step 1: Enable GDM3
```bash
sudo systemctl enable gdm3
sudo systemctl set-default graphical.target
```

### Step 2: Restart
```bash
sudo reboot
```

**Verification:**
```bash
systemctl get-default  # graphical.target
# You should see graphical login
```

## Alternatives and Tips
- **Change without restart:** Use `sudo systemctl isolate multi-user.target` (temporary).
- **Other DM:** If you prefer LightDM: `sudo apt install lightdm && sudo dpkg-reconfigure lightdm`.
- **GPU issues:** If black screen, force Xorg in `/etc/gdm3/custom.conf` (see section 3).

## Troubleshooting
- **GDM3 not starting:** Logs: `sudo journalctl -u gdm`.
- **Black screen:** Add `nomodeset` in GRUB (see section 2).
- **Target not changing:** `sudo systemctl daemon-reload` and retry.

> **Explanation:** Disabling frees RAM/CPU; reactivating for GUI apps. Use as needed.

---

> [Index](../../README_en.md#index) · [Previous: 7. Specific Setup for Analytics Workstations](07-analytics-workstations.md) · [Next: 9. Common Network Issues with New Motherboards](09-network-issues.md) · [Español](../08-interfaz-grafica.md)
