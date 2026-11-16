# 13. Buenas Prácticas de Seguridad (Opcional)

> [Índice](../README.md#índice) · [Anterior: 12. Scripts Doctor de Verificación](12-scripts-doctor.md) · [Siguiente: 14. Runbook: MongoDB 8 no arranca por kernel HWE 7.0](14-runbook-mongodb8-kernel.md) · [English](en/13-security.md)

> **Nota:** Estas medidas fortalecen Ubuntu, especialmente para acceso remoto. Aplica solo lo necesario; más seguridad puede complicar uso.

## SSH Seguro

### Cambiar Puerto SSH
Reduce escaneo de bots.

1. Edita config: `sudo nano /etc/ssh/sshd_config`
2. Cambia: `Port 22` a `Port 2222`
3. Reinicia SSH: `sudo systemctl restart ssh`
4. Firewall: `sudo ufw allow 2222/tcp && sudo ufw delete allow 22/tcp`

**Verificación (opcional):** `ss -tlnp | grep 2222`

### Autenticación por Clave SSH
Deshabilita passwords.

1. Genera clave local: `ssh-keygen -t ed25519 -C "tu_email"`
2. Copia a servidor: `ssh-copy-id -p 2222 usuario@ip_servidor`
3. Deshabilita password: `sudo nano /etc/ssh/sshd_config` > `PasswordAuthentication no`
4. Reinicia: `sudo systemctl restart ssh`

**Verificación (opcional):** Intenta login con password (debe fallar).

### Deshabilitar Root Login
Previene acceso directo como root.

1. Edita: `sudo nano /etc/ssh/sshd_config` > `PermitRootLogin no`
2. Reinicia: `sudo systemctl restart ssh`

## Firewall y Monitoreo

### Instalar Fail2Ban
Bloquea IPs con intentos fallidos.

1. Instala: `sudo apt install fail2ban`
2. Habilita: `sudo systemctl enable fail2ban`
3. Config: `sudo nano /etc/fail2ban/jail.local` (ej. `[sshd]` con `port = 2222`)

**Verificación (opcional):** `sudo fail2ban-client status sshd`

### Actualizaciones Automáticas
Mantén sistema seguro.

1. Instala unattended-upgrades: `sudo apt install unattended-upgrades`
2. Config: `sudo dpkg-reconfigure unattended-upgrades`
3. O cron (solo para actualizaciones de seguridad): `sudo crontab -e` > `0 2 * * * apt update && apt upgrade -y`
   > **Advertencia:** No usar `apt upgrade -y` automático en producción con drivers NVIDIA. Una actualización de kernel puede romper los módulos NVIDIA. Prefiere `unattended-upgrades` que maneja esto mejor.

**Verificación (opcional):** `sudo unattended-upgrades --dry-run`

## Otras Prácticas

- **Backups:** Usa `rsync` o `borgbackup` para backups.
- **Antivirus:** Instala `clamav` para scans: `sudo apt install clamav`
- **Logs:** Monitorea con `journalctl` o `logwatch`.
- **VPN:** Usa WireGuard para acceso remoto seguro.

## Troubleshooting
- **SSH no conecta:** Verifica puerto y firewall.
- **Fail2Ban bloquea:** `sudo fail2ban-client unban <IP>`
- **Updates fallan:** `sudo apt --fix-broken install`

> **Tip:** Usa herramientas como `lynis` para auditoría: `sudo apt install lynis && sudo lynis audit system`

---

> [Índice](../README.md#índice) · [Anterior: 12. Scripts Doctor de Verificación](12-scripts-doctor.md) · [Siguiente: 14. Runbook: MongoDB 8 no arranca por kernel HWE 7.0](14-runbook-mongodb8-kernel.md) · [English](en/13-security.md)
