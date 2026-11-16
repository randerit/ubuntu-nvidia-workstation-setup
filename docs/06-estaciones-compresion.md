# 6. Configuración Específica para Estaciones de Compresión

> [Índice](../README.md#índice) · [Anterior: 5. Instalación de CUDA Toolkit](05-cuda-toolkit.md) · [Siguiente: 7. Configuración Específica para Estaciones de Analítica](07-estaciones-analitica.md) · [English](en/06-compression-workstations.md)

> **Nota:** Esta sección instala herramientas para estaciones de compresión/data, asumiendo Ubuntu 24.04.1 LTS con CUDA/drivers instalados. Las herramientas son opcionales; instala solo lo necesario. Verifica versiones en sitios oficiales.

## Instalación de MongoDB (Base de Datos NoSQL)

### Paso 0: Verifica que el kernel sea compatible

MongoDB 8 **no arranca** en kernels Linux 6.19 – 7.0.13 (bug de TCMalloc/rseq,
[SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). Antes de instalar:

```bash
uname -r                        # esperado: 6.8.0-1XX-generic
cat /proc/version_signature     # base upstream real, p.ej. "... 6.8.0-136.136"
```

- Si ves `6.8.0-1XX-generic`, sigue con el Paso 1. Si aún no aplicaste el pinning preventivo del
  [Paso 7 de la Sección 3](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu), hazlo ahora — sin
  él, un `apt upgrade` futuro reinstala el HWE y deja el equipo sin base de datos.
- Si ves `7.0.0-XX-generic`, **no instales MongoDB todavía**: ve a la
  [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70) y vuelve acá al terminar.

### Paso 1: Agrega el Repositorio
Importa la clave GPG:
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg
```

Agrega el repositorio (ajusta `jammy` por `noble` si usas Ubuntu 24.04):
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

### Paso 2: Instala MongoDB
```bash
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### Paso 3: Inicia y Habilita el Servicio
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Verificación (opcional):**
```bash
sudo systemctl status mongod
mongosh --eval "db.runCommand('ping')"
# Debería mostrar "ok": 1
```

> **Nota sobre Transparent Huge Pages:** MongoDB 8.0 requiere THP **habilitado**, al revés que
> 7.0 y anteriores. Si algún script de provisión antiguo dejó `transparent_hugepage=never` en
> `GRUB_CMDLINE_LINUX` o una unit de systemd que lo desactiva, quítalo. Verifica con
> `cat /sys/kernel/mm/transparent_hugepage/enabled` (debería mostrar `[always]` o `[madvise]`).

## Instalación de MongoDB Compass (GUI para MongoDB)

### Paso 1: Descarga e Instala
Descarga desde [https://www.mongodb.com/try/download/compass](https://www.mongodb.com/try/download/compass):
```bash
wget https://downloads.mongodb.com/compass/mongodb-compass_1.49.15_amd64.deb
sudo apt install -y ./mongodb-compass_1.49.15_amd64.deb
```

Si dependencias faltan:
```bash
sudo apt --fix-broken install
```

### Paso 2: Ejecuta Compass
```bash
mongodb-compass &
```

**Verificación (opcional):** Abre la app y conecta a `mongodb://localhost:27017`.

**Desinstalación (opcional):**
```bash
sudo apt remove -y mongodb-compass
```

## Instalación de EMQX (Broker MQTT)

### Paso 1: Instala desde Repositorio
> **Advertencia de seguridad:** Revisa el contenido del script antes de ejecutarlo con `sudo`. Puedes descargarlo primero con `wget` e inspeccionarlo.

```bash
curl -sL https://assets.emqx.com/scripts/install-emqx-deb.sh | sudo bash
sudo apt-get install -y emqx
```

### Paso 2: Inicia y Habilita
```bash
sudo systemctl start emqx
sudo systemctl enable emqx
```

**Verificación (opcional):**
```bash
sudo systemctl status emqx
# Dashboard en http://localhost:18083 (credenciales iniciales de EMQX: admin / public; cámbialas en el primer ingreso)
```

> **Si `emqx` queda instalado pero el servicio no arranca:** EMQX 5 no levanta sin
> `/etc/emqx/acl.conf`. Ese archivo es un *conffile* de dpkg, y dpkg interpreta su
> ausencia como decision del administrador: si alguien lo borro o lo movio, no lo
> repone ni la instalacion ni un `--reinstall` normal. La unica forma de traerlo de
> vuelta desde el paquete es `--force-confmiss`:
>
> ```bash
> ls -l /etc/emqx/acl.conf     # si no existe, es esto
> sudo apt-get install -y --reinstall -o Dpkg::Options::=--force-confmiss emqx
> sudo systemctl start emqx && systemctl is-active emqx
> ```

## Instalación de Golang

### Paso 1: Instala con Snap
```bash
sudo snap install go --classic
```

**Verificación (opcional):**
```bash
go version
# Debería mostrar versión instalada
```

## Instalación de Visual Studio Code

### Paso 1: Instala con Snap
```bash
sudo snap install code --classic
```

**Verificación (opcional):**
```bash
code --version
# Debería mostrar versión
```

## Instalación de GStreamer y Plugins

### Paso 1: Instala Plugins
```bash
sudo apt-get install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio gstreamer1.0-rtsp
```

**Verificación (opcional):**
```bash
gst-inspect-1.0 rtspclientsink
gst-inspect-1.0 nvh264enc
# Debería mostrar info del plugin
```

## Instalación de Angry IP Scanner

### Paso 1: Descarga e Instala
Descarga desde [https://github.com/angryip/ipscan/releases](https://github.com/angryip/ipscan/releases):
```bash
wget https://github.com/angryip/ipscan/releases/download/3.9.1/ipscan_3.9.1_amd64.deb
sudo apt install -y ./ipscan_3.9.1_amd64.deb
```

**Verificación (opcional):** Ejecuta `ipscan` desde terminal o menú.

## Instalación de AnyDesk (Soporte Remoto)

### Paso 1: Agrega Repositorio e Instala
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

### Paso 2: Configura el servicio para compatibilidad con NVIDIA y X11

> **Importante:** En equipos con driver NVIDIA instalado por `.run` y Xorg forzado, el servicio de AnyDesk arranca como `root` sin acceso al display X11 del usuario. Sin este fix, AnyDesk crashea al inicio y genera un loop de CPU que congela el escritorio GNOME. Este paso es obligatorio en estaciones de compresión.

Crea el override del servicio:

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

Aplica los cambios:

```bash
sudo systemctl daemon-reload
sudo systemctl enable anydesk
sudo systemctl start anydesk
```

**Verificación (opcional):**
```bash
sudo systemctl status anydesk
# Debería mostrar "active (running)" sin errores
sudo systemctl cat anydesk | grep -A6 "override.conf"
# Debería mostrar las 4 líneas del override
```

### Paso 3: Configura Firewall
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 6568/tcp
sudo ufw allow 50001:50003/udp
```

**Verificación (opcional):** Ejecuta `anydesk` desde el escritorio y anota el ID.

## Instalación de RustDesk (Soporte Remoto Alternativo)

### Paso 1: Descarga e Instala
Descarga desde [https://github.com/rustdesk/rustdesk/releases](https://github.com/rustdesk/rustdesk/releases):
```bash
wget https://github.com/rustdesk/rustdesk/releases/download/1.2.3/rustdesk-1.2.3-x86_64.deb
sudo apt install -y ./rustdesk-1.2.3-x86_64.deb
```

**Verificación (opcional):** Ejecuta `rustdesk` y configura ID/contraseña.

## Configuración de Puertos para Estaciones de Compresión (Opcional)
Si habilitaste UFW en la sección 3, abre los puertos necesarios para que las aplicaciones funcionen correctamente. Si no usas firewall, omite esta sección.

| Aplicación | Puertos | Protocolo | Comando para Abrir (Opcional) |
|------------|---------|-----------|-------------------------------|
| MongoDB | 27017 | TCP | `sudo ufw allow 27017/tcp` |
| EMQX MQTT | 1883 | TCP | `sudo ufw allow 1883/tcp` |
| EMQX Dashboard | 18083 | TCP | `sudo ufw allow 18083/tcp` |
| GStreamer RTSP | 554 | TCP/UDP | `sudo ufw allow 554/tcp && sudo ufw allow 554/udp` |
| AnyDesk | 80, 443, 6568 | TCP | `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw allow 6568/tcp` |
| AnyDesk (UDP) | 50001-50003 | UDP | `sudo ufw allow 50001:50003/udp` |
| RustDesk | Dinámicos (ver logs) | TCP/UDP | Configura según necesidad |
| SSH (si usas) | 22 (o custom) | TCP | `sudo ufw allow ssh` |

**Verificación general (opcional):**
```bash
sudo ufw status
netstat -tlnp | grep LISTEN  # Lista puertos abiertos
```

**Tips (opcional):**
- Para acceso remoto, abre solo puertos necesarios y desde IPs específicas: `sudo ufw allow from <IP> to any port 27017`.
- Si usas VPN, ajusta reglas.
- Revisa logs de apps para puertos adicionales (ej. `sudo journalctl -u emqx`).

## Tips Generales
- Verifica servicios: `sudo systemctl status <servicio>`.
- Configura contraseñas únicas para acceso remoto.
- Revisa plugins: Usa `gst-inspect-1.0` para GStreamer.

## Troubleshooting
- **MongoDB no inicia:** Revisa logs: `sudo journalctl -u mongod`.
- **MongoDB no inicia y el journal dice `MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility`:** El equipo está corriendo el kernel HWE 7.0. Confirma con `uname -r` y aplica la [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70). No sirve reinstalar `mongodb-org` ni tocar `/etc/mongod.conf`.
- **EMQX falla:** Verifica puertos: `netstat -tlnp | grep 1883`.
- **EMQX instalado pero el servicio muerto y falta `/etc/emqx/acl.conf`:** dpkg no repone un conffile borrado o movido. `sudo apt-get install -y --reinstall -o Dpkg::Options::=--force-confmiss emqx`, luego `sudo systemctl start emqx`. `workstation-doctor-compresion` detecta y corrige este caso.
- **GStreamer plugins faltan:** `sudo apt install gstreamer1.0-plugins-*`.
- **AnyDesk/RustDesk no conecta:** Desactiva firewall temporalmente para test.
- **AnyDesk congela el escritorio al iniciar (gnome-shell al 70–100% CPU):** El servicio de AnyDesk no tiene acceso al display X11. Verifica que el override del Paso 2 esté aplicado con `sudo systemctl cat anydesk`. Si no aparece el bloque `override.conf`, repite el Paso 2 y ejecuta `sudo systemctl daemon-reload && sudo systemctl restart anydesk`. Síntoma adicional: aparece `_usr_bin_anydesk.1000.crash` en `/var/crash/`.
- **AnyDesk muestra "Authorization required, but no authorization protocol specified":** El servicio arranca antes de que X11 esté listo o sin las variables `DISPLAY`/`XAUTHORITY`. El `ExecStartPre=/bin/sleep 5` del override corrige el timing; verifica que esté presente.

> **Recursos Adicionales:**
> * [MongoDB Docs](https://www.mongodb.com/docs/)
> * [EMQX Docs](https://www.emqx.io/docs/)
> * [GStreamer Docs](https://gstreamer.freedesktop.org/documentation/)

---

> [Índice](../README.md#índice) · [Anterior: 5. Instalación de CUDA Toolkit](05-cuda-toolkit.md) · [Siguiente: 7. Configuración Específica para Estaciones de Analítica](07-estaciones-analitica.md) · [English](en/06-compression-workstations.md)
