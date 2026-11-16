# 13. Security Best Practices (Optional)

> [Index](../../README_en.md#index) · [Previous: 12. Doctor Verification Scripts](12-doctor-scripts.md) · [Next: 14. Runbook: MongoDB 8 Fails to Start on HWE Kernel 7.0](14-runbook-mongodb8-kernel.md) · [Español](../13-seguridad.md)

> **Note:** These measures strengthen Ubuntu, especially for remote access. Apply only what's necessary; more security may complicate use.

## Secure SSH

### Change SSH Port
Reduce bot scans.

1. Edit config: `sudo nano /etc/ssh/sshd_config`
2. Change: `Port 22` to `Port 2222`
3. Restart SSH: `sudo systemctl restart ssh`
4. Firewall: `sudo ufw allow 2222/tcp && sudo ufw delete allow 22/tcp`

**Verification:** `ss -tlnp | grep 2222`

### SSH Key Authentication
Disable passwords.

1. Generate local key: `ssh-keygen -t ed25519 -C "your_email"`
2. Copy to server: `ssh-copy-id -p 2222 user@server_ip`
3. Disable password: `sudo nano /etc/ssh/sshd_config` > `PasswordAuthentication no`
4. Restart: `sudo systemctl restart ssh`

**Verification:** Try login with password (should fail).

### Disable Root Login
Prevent direct root access.

1. Edit: `sudo nano /etc/ssh/sshd_config` > `PermitRootLogin no`
2. Restart: `sudo systemctl restart ssh`

## Firewall and Monitoring

### Install Fail2Ban
Block IPs with failed attempts.

1. Install: `sudo apt install fail2ban`
2. Enable: `sudo systemctl enable fail2ban`
3. Config: `sudo nano /etc/fail2ban/jail.local` (e.g., `[sshd]` with `port = 2222`)

**Verification:** `sudo fail2ban-client status sshd`

### Automatic Updates
Keep system secure.

1. Install unattended-upgrades: `sudo apt install unattended-upgrades`
2. Config: `sudo dpkg-reconfigure unattended-upgrades`
3. Or cron (security updates only): `sudo crontab -e` > `0 2 * * * apt update && apt upgrade -y`
   > **Warning:** Do not use an automatic `apt upgrade -y` in production with NVIDIA drivers. A kernel update can break the NVIDIA modules. Prefer `unattended-upgrades`, which handles this better.

**Verification:** `sudo unattended-upgrades --dry-run`

## Other Practices

- **Backups:** Use `rsync` or `borgbackup` for backups.
- **Antivirus:** Install `clamav` for scans: `sudo apt install clamav`
- **Logs:** Monitor with `journalctl` or `logwatch`.
- **VPN:** Use WireGuard for secure remote access.

## Troubleshooting
- **SSH not connecting:** Check port and firewall.
- **Fail2Ban blocking:** `sudo fail2ban-client unban <IP>`
- **Updates failing:** `sudo apt --fix-broken install`

> **Tip:** Use tools like `lynis` for audit: `sudo apt install lynis && sudo lynis audit system`

---

> [Index](../../README_en.md#index) · [Previous: 12. Doctor Verification Scripts](12-doctor-scripts.md) · [Next: 14. Runbook: MongoDB 8 Fails to Start on HWE Kernel 7.0](14-runbook-mongodb8-kernel.md) · [Español](../13-seguridad.md)
