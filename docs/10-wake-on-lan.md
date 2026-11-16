# 10. Wake-on-LAN (WOL): Windows a Windows y Ubuntu a Windows

> [Índice](../README.md#índice) · [Anterior: 9. Solución de Problemas Comunes con Redes en Placas Nuevas](09-redes-placas-nuevas.md) · [Siguiente: 11. Script de Post-Instalación (Opcional)](11-script-post-instalacion.md) · [English](en/10-wake-on-lan.md)

> **Nota:** WOL despierta PCs por red enviando un "paquete mágico". Requiere Ethernet (no Wi-Fi). Configura BIOS y OS primero.

## Configurar WOL en el Equipo Destino (Windows/Ubuntu)

### En BIOS/UEFI
1. Entra a BIOS (F2/DEL).
2. Busca "Power Management" > "Wake on LAN" > "Enabled".
3. "AC Power Loss" > "Power On" (opcional).
4. Guarda y sal.

### En Windows
1. Ejecuta `powercfg /devicequery wake_armed` (lista dispositivos que pueden despertar).
2. En Device Manager > Network Adapter > Properties > Power Management > Marca "Allow this device to wake the computer".
3. En Power Options > "Allow wake timers".

### En Ubuntu
1. Instala ethtool: `sudo apt install ethtool`
2. Habilita WOL: `sudo ethtool -s enpXsY wol g` (reemplaza enpXsY por interfaz, ej. `ip link show`)
3. Verifica: `sudo ethtool enpXsY | grep Wake-on`
4. Para persistencia: Crea `/etc/systemd/system/wol.service` con:
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
   Habilita: `sudo systemctl enable wol`

**Verificación (opcional):** Apaga el PC, espera 1 min, envía paquete desde otro dispositivo.

## Enviar Paquete WOL desde Windows (a Windows o Ubuntu)

### Script PowerShell
Guarda como `Send-WOL.ps1` y ejecuta: `.\Send-WOL.ps1 -Mac AA:BB:CC:DD:EE:FF`

Funciona para despertar PCs Windows o Ubuntu configurados para WOL.

```powershell
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)] [string]$Mac,
  [string]$Broadcast = "255.255.255.255",
  [int]$Port = 9
)

$macClean = ($Mac -replace '[:-]','')
if ($macClean.Length -ne 12) { throw "MAC inválida: $Mac" }

$macBytes = 0..5 | ForEach-Object { [Convert]::ToByte($macClean.Substring($_*2,2),16) }

$packet = New-Object byte[] (6 + 16*6)
for ($i=0; $i -lt 6; $i++) { $packet[$i] = 0xFF }
for ($i=0; $i -lt 16; $i++) { [Array]::Copy($macBytes, 0, $packet, 6 + $i*6, 6) }

$udp = New-Object System.Net.Sockets.UdpClient
$udp.EnableBroadcast = $true
[void]$udp.Send($packet, $packet.Length, $Broadcast, $Port)
$udp.Close()
Write-Host "WOL enviado a $Mac via $Broadcast:$Port"
```

## Enviar Paquete WOL desde Ubuntu

### Instala herramientas
```bash
sudo apt install wakeonlan etherwake
```

### Envía paquete
```bash
wakeonlan -i 192.0.2.255 AA:BB:CC:DD:EE:FF  # Broadcast IP de tu red
# o
sudo etherwake -i enpXsY AA:BB:CC:DD:EE:FF
```

**Verificación (opcional):** Usa Wireshark/tcpdump para ver paquete: `sudo tcpdump -i enpXsY port 9`

## Troubleshooting
- **No despierta:** Verifica BIOS, cable Ethernet, firewall bloquea puerto 9.
- **MAC incorrecta:** `ip link show` o `arp -a` para obtener.
- **Broadcast IP:** Usa `ip route | grep default` para subnet.
- **Persistencia:** En Ubuntu, agrega a cron: `@reboot sudo ethtool -s enpXsY wol g`

> **Nota:** WOL por Wi-Fi no funciona. Usa Ethernet. Prueba con PCs en misma red local.

---

> [Índice](../README.md#índice) · [Anterior: 9. Solución de Problemas Comunes con Redes en Placas Nuevas](09-redes-placas-nuevas.md) · [Siguiente: 11. Script de Post-Instalación (Opcional)](11-script-post-instalacion.md) · [English](en/10-wake-on-lan.md)
