# 9. Solución de Problemas Comunes con Redes en Placas Nuevas

> [Índice](../README.md#índice) · [Anterior: 8. Gestión de la Interfaz Gráfica](08-interfaz-grafica.md) · [Siguiente: 10. Wake-on-LAN (WOL): Windows a Windows y Ubuntu a Windows](10-wake-on-lan.md) · [English](en/09-network-issues.md)

> **Nota:** Problemas de red en placas nuevas suelen ser por drivers incompatibles. Usa `lspci | grep Network` para identificar el chip. Reinicia después de cambios.

> **⚠️ Antes de instalar el kernel HWE para resolver una NIC:** en cualquier estación que corra
> MongoDB 8 —o sea, todas las de compresión y analítica— ese camino está **cerrado**. El kernel HWE
> de 24.04 arrastra la serie 7.0, que impide arrancar `mongod`
> ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)), y el pin de la
> [Sección 3 Paso 7](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu) lo deja sin candidato: el
> `apt install` va a fallar con `has no installation candidate`.
>
> Lo que hace falta es un **driver** más nuevo, no un kernel más nuevo. El procedimiento completo,
> con el orden correcto para no quedarte sin red a mitad de camino, está en el
> [Caso C de la Sección 14](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga).

## Problemas con Realtek RTL8125 (Ethernet)

### Diagnóstico
```bash
ip link show  # Busca ethX/enpXsY DOWN
lspci | grep RTL8125  # Confirma chip
```

### Solución

Primero mirá la revisión del chip, porque decide todo lo demás:

```bash
lspci -nn | grep -i 8125             # confirma el PCI ID (10ec:8125)
dmesg | grep -iE 'r8169|r8125|XID'   # la revision aparece como "XID <n>"
```

| Revisión | XID | Qué la maneja |
|---|---|---|
| RTL8125A / B / C | 605, 641, 648… | El `r8169` in-tree del GA 6.8, solo. No toques nada |
| **RTL8125D** | **688** | Ni el `r8169` del GA ni el `r8125-dkms` de Ubuntu. Ver abajo |

> **`r8169` activo no es, por sí solo, un problema.** Es el driver correcto para las revisiones
> A/B/C en cualquier kernel, y para **todas** —incluida la D— en los kernels HWE 7.x, donde el
> soporte ya está in-tree. El único caso en que `r8169` es el driver equivocado es **RTL8125D
> (XID 688) sobre el track GA 6.8**. Diagnosticar "hay que instalar r8125" con solo ver `r8169` es
> el falso positivo clásico de esta sección.

Si la interfaz está UP y `basename $(readlink -f /sys/class/net/<iface>/device/driver)` dice
`r8169`, ya funciona: no instales nada.

Para las A/B/C que no levanten, el paquete de los repos de Ubuntu alcanza:

```bash
sudo apt update
sudo apt install -y dkms build-essential linux-headers-generic
sudo apt install -y r8125-dkms        # para RTL8168/8111 usa r8168-dkms
```

> **Antes de instalar `r8125-dkms` en un equipo que vas a bajar al GA:** ese paquete (9.011.00)
> deja un `r8125.ko` en `updates/dkms/` que **no** soporta el RTL8125D, y con eso el chequeo
> pre-reboot del [Caso C](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga) da verde con una
> placa que igual va a quedarse sin red. Si la placa es rev D o no podés determinar la revisión, no
> pases por acá: andá directo al driver del fabricante (≥ 9.014.01) o a `sudo nic-driver-rescue`.

> **Para el RTL8125D (XID 688) ese paquete no sirve.** noble trae `r8125-dkms` 9.011.00, cuyo
> código de detección solo cubre hasta la revisión C y manda el XID 688 a `unknown chip version`.
> Hace falta el driver del fabricante, versión **9.014.01 o superior**. El procedimiento completo
> —con el orden correcto para no quedarte sin red a mitad de camino— está en
> [Caso C de la Sección 14](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga).

> **No blacklistees `r8169`.** Es un reflejo común y acá hace daño: las RTL8168/8111 (`10ec:8168`)
> dependen de él, y en placas de dos puertos suele ser el único enlace que funciona. Tampoco hace
> falta: los dos módulos declaran el alias del `10ec:8125`, así que `modprobe` carga los dos y el
> device se lo queda **el primero cuyo probe funcione**. El `r8169` viene en el initramfs y llega
> antes, así que se queda con las revisiones que soporta y el `r8125` queda cargado sin usar; con
> las que no soporta falla el probe, libera el device y ahí lo toma el `r8125`.

Al ser DKMS, el módulo se recompila en cada cambio de kernel, así que este camino es compatible con
el pin del track GA que exige MongoDB 8.

**Verificación (opcional):** `ip link show` (debería estar UP), `lspci | grep -i ethernet`

## Problemas con Intel Ethernet (ej. I219, I225, I226)

### Diagnóstico
```bash
lspci | grep -i ethernet              # Busca controlador Intel
dmesg | grep -Ei 'e1000e|igc|igb'     # Errores del driver
ip link show                          # Estado UP/DOWN de la interfaz
```

Los chips Intel I219 usan el driver `e1000e`, mientras que I225/I226 usan `igc`. Ambos vienen incluidos en el kernel de Ubuntu; el problema casi siempre es un kernel demasiado antiguo o firmware faltante.

### Solución

1. Actualiza el sistema y firmware:
   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y linux-firmware
   ```
2. Confirmá si el driver del kernel que vas a usar conoce tu placa. Sacá el PCI ID de
   `lspci -nn` —por ejemplo `8086:125c`— y preguntale al módulo:
   ```bash
   lspci -nn | grep -Ei 'ethernet'
   modinfo igc | grep -i 'pci:v00008086d0000125C'   # ajusta el ID al de tu placa
   ```
   Si el alias aparece, el driver soporta el chip y el problema es otro: firmware, BIOS o el punto 4.
3. Si el alias **no** aparece, el driver de ese kernel es demasiado viejo para la placa.

   > **No instales `linux-generic-hwe-24.04` si la estación corre MongoDB 8.** Ese es el kernel de la
   > serie 7.0 que impide arrancar `mongod`. Seguí el
   > [Caso C de la Sección 14](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga), que resuelve la
   > NIC sin cambiar de track de kernel.

   En un equipo que **no** vaya a correr MongoDB, el HWE sigue siendo válido:
   ```bash
   sudo apt install -y --install-recommends linux-generic-hwe-24.04
   ```
   Para Ubuntu 22.04 usa `linux-generic-hwe-22.04`.
4. Si el chip levanta pero la conexión es inestable y `dmesg` muestra errores de `igc`, probá
   desactivar TSO/GSO temporalmente:
   ```bash
   sudo ethtool -K enpXsY tso off gso off gro off
   ```

**Verificación (opcional):** `ip a` (IP asignada), `ping 8.8.8.8`

> **Nota:** El paquete `backport-iwlwifi-dkms` es para tarjetas **Wi-Fi** Intel (chipset `iwlwifi`), no para Ethernet. No lo instales para resolver problemas de I219/I225/I226.

## Problemas con Wi-Fi (Broadcom, etc.)

### Diagnóstico
```bash
iwconfig  # Lista interfaces Wi-Fi
lspci | grep Network  # Identifica chip
```

### Solución para Broadcom
1. Instala bcmwl: `sudo apt install bcmwl-kernel-source`
2. Reinicia: `sudo reboot`

**Verificación (opcional):** `iwconfig` (debería mostrar wlan0 UP)

## DNS No Resuelve Nombres

### Diagnóstico
```bash
nslookup google.com  # Falla?
cat /etc/resolv.conf  # Nameservers
```

### Solución
1. Edita resolv.conf: `sudo nano /etc/resolv.conf`
2. Agrega: `nameserver 8.8.8.8` y `nameserver 1.1.1.1`
3. O usa systemd: `sudo systemctl restart systemd-resolved`

**Verificación (opcional):** `nslookup google.com` (debería resolver)

## Conexión Lenta o Intermitente

### Diagnóstico
```bash
speedtest-cli  # Velocidad
dmesg | grep -i network  # Errores
```

### Solución
1. Desactiva IPv6: `sudo nano /etc/sysctl.conf` agrega `net.ipv6.conf.all.disable_ipv6=1`
2. Aplica: `sudo sysctl -p`
3. Cambia MTU: `sudo ip link set dev enpXsY mtu 1450`

**Verificación (opcional):** `speedtest-cli`, reinicia y testea.

## Configurar IP Estática

### Solución
1. Edita Netplan: `sudo nano /etc/netplan/01-netcfg.yaml`
2. Ejemplo (direcciones de documentación; usa las de tu red):
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
   > **Nota:** `gateway4` está deprecado desde Netplan 0.105+. Usa `routes` como se muestra arriba.
3. Aplica: `sudo netplan apply`

**Verificación (opcional):** `ip a` (IP estática), `ping google.com`

## Problemas con VPN

### Diagnóstico
```bash
sudo systemctl status openvpn  # Si usas OpenVPN
journalctl -u openvpn  # Logs
```

### Solución
1. Instala OpenVPN: `sudo apt install openvpn`
2. Conecta: `sudo openvpn config.ovpn`
3. Para WireGuard: `sudo apt install wireguard` y configura.

**Verificación (opcional):** `ip a` (tun interface), `curl ifconfig.me` (IP externa cambia)

## Troubleshooting General
- **No conecta:** `sudo systemctl restart NetworkManager`
- **Drivers faltan:** Busca en repos: `sudo apt search <chip>`
- **Logs:** `sudo journalctl -u NetworkManager`
- **Reset:** `sudo nmcli networking off && sudo nmcli networking on`

> **Tip:** Si nada funciona, instala drivers desde sitio del fabricante o usa USB Ethernet.

---

> [Índice](../README.md#índice) · [Anterior: 8. Gestión de la Interfaz Gráfica](08-interfaz-grafica.md) · [Siguiente: 10. Wake-on-LAN (WOL): Windows a Windows y Ubuntu a Windows](10-wake-on-lan.md) · [English](en/09-network-issues.md)
