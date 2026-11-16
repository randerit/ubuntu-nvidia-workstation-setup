# 3. Preparación Inicial del Sistema Ubuntu

> [Índice](../README.md#índice) · [Anterior: 2. Instalación del Sistema Ubuntu](02-instalacion-ubuntu.md) · [Siguiente: 4. Instalación de Drivers de NVIDIA en Ubuntu](04-drivers-nvidia.md) · [English](en/03-system-preparation.md)

Esta sección deja Ubuntu listo para instalar el driver NVIDIA oficial con archivo `.run`, que será el camino principal de este manual. Todavía no instales el driver NVIDIA ni CUDA; eso viene en las secciones siguientes.

## Regla de esta sección

- Sí instalamos actualizaciones, herramientas de compilación, headers del kernel y utilidades base.
- Sí dejamos el entorno gráfico en Xorg para evitar conflictos con NVIDIA.
- Sí podemos instalar firmware o drivers de **Ethernet/Wi-Fi** si la red no funciona.
- No usamos `ubuntu-drivers`, "Additional Drivers" ni repositorios APT para instalar NVIDIA.
- No ejecutamos todavía ningún instalador `.run`.

## Paso 1: Abre una terminal

Presiona `Ctrl+Alt+T`.

Si el equipo pide contraseña al usar `sudo`, escribe la contraseña de tu usuario. La terminal no mostrará caracteres mientras la escribes; eso es normal.

## Paso 2: Verifica internet y drivers de red

Antes de actualizar Ubuntu, confirma que el equipo tiene red:

```bash
nmcli device status
ping -c 4 archive.ubuntu.com
```

Resultado esperado:

- `nmcli` muestra al menos una interfaz conectada.
- `ping` recibe respuestas.

Si **Ethernet o Wi-Fi no aparecen**, identifica el hardware:

```bash
lspci -nn | grep -Ei 'ethernet|network|wireless|wifi'
lsusb
```

Usa esta salida para decidir:

| Caso | Qué hacer |
|------|-----------|
| Ethernet funciona, Wi-Fi no | Conecta cable Ethernet y sigue con la guía. El Wi-Fi se puede resolver después. |
| Wi-Fi funciona, Ethernet no | Conéctate por Wi-Fi y sigue con la guía. Ethernet se puede resolver después. |
| No funciona ni Ethernet ni Wi-Fi | Usa internet temporal por USB tethering desde un teléfono o un adaptador USB Ethernet/Wi-Fi compatible con Linux. |
| Aparece Broadcom Wi-Fi | Con internet temporal, instala `bcmwl-kernel-source`. |
| Aparece Intel/Realtek Wi-Fi pero no conecta | Con internet temporal, instala o actualiza `linux-firmware`. |
| Aparece Realtek RTL8125 Ethernet | Si no levanta red, revisa la sección 9 después de conseguir internet temporal. |

Con internet temporal, instala firmware base de red:

```bash
sudo apt update
sudo apt install -y linux-firmware
sudo reboot
```

> **Importante:** Está permitido usar "Additional Drivers" para controladores de red como Broadcom Wi-Fi. No selecciones drivers NVIDIA ahí; NVIDIA se instalará en la sección 4 con `.run`.

## Paso 3: Actualiza Ubuntu y reinicia

Primero actualiza el sistema completo:

```bash
sudo apt update
sudo apt upgrade -y
```

Cuando termine, reinicia:

```bash
sudo reboot
```

Después del reinicio, vuelve a abrir la terminal.

## Paso 4: Instala herramientas necesarias para `.run`

El instalador `.run` de NVIDIA necesita compilar módulos para el kernel. Para eso se requieren headers, DKMS y herramientas de compilación.

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r) linux-headers-generic pkg-config gcc g++ make
sudo apt install -y libglvnd-dev libgl1-mesa-dev libegl1-mesa-dev libgles2-mesa-dev libx11-dev libxmu-dev libxi-dev libglu1-mesa-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
sudo apt install -y ca-certificates curl wget git vim nano mesa-utils inxi net-tools openssh-server ufw dnsutils htop ncdu tree traceroute nmap lm-sensors neofetch
```

## Paso 5: Desactiva Wayland y usa Xorg

Para este manual usaremos Xorg porque suele ser más predecible con drivers NVIDIA instalados por `.run`.

Edita la configuración de GDM3:

```bash
sudo nano /etc/gdm3/custom.conf
```

Busca esta línea:

```ini
#WaylandEnable=false
```

Déjala así, sin `#` al inicio:

```ini
WaylandEnable=false
```

Guarda con `Ctrl+O`, presiona `Enter` y sal con `Ctrl+X`.

Reinicia para aplicar el cambio:

```bash
sudo reboot
```

## Paso 6: Prepara acceso remoto si lo vas a usar

Si el equipo será administrado desde otra máquina, activa SSH y permite el acceso en el firewall:

```bash
sudo systemctl enable --now ssh
sudo ufw allow ssh
sudo ufw --force enable
```

Si no usarás acceso remoto, puedes saltar este paso.

> **Un firewall activo con las reglas a medias corta servicios.** Acá UFW queda arriba
> con solo SSH permitido, que es correcto en este punto porque todavía no hay nada más
> instalado. Los puertos del stack (MongoDB, MQTT, dashboard de EMQX, RTSP, Node-RED,
> AnyDesk) se agregan en las Secciones 6 y 7. Si el equipo va a correr esos servicios,
> **no lo dejes acá**: con UFW activo y un puerto sin permitir, el servicio arranca bien
> y aun así es inalcanzable desde la red, y el diagnóstico se va al servicio en lugar
> del firewall. Verificá qué hay permitido con `sudo ufw show added` (funciona incluso
> con el firewall apagado; `sudo ufw status` no lista nada si está inactivo).

## Paso 7: Aplica ajustes según tu versión de Ubuntu

Primero mira tu versión:

```bash
lsb_release -rs
```

> **En Linux Mint** este comando devuelve la versión de Mint (por ejemplo `22.1`), no la de
> Ubuntu. La base es la que manda: sácala de `/etc/upstream-release/lsb-release` y aplica los
> ajustes de esa versión.

Para **Ubuntu 22.04 LTS**, instala GCC/G++ 12 si vas a usar versiones de CUDA que lo requieran:

```bash
sudo apt install -y gcc-12 g++-12
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 120
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-12 120
```

Para **Ubuntu 24.04 LTS**, instala `libtinfo5` solo si CUDA o una herramienta antigua lo solicita:

```bash
wget http://security.ubuntu.com/ubuntu/pool/universe/n/ncurses/libtinfo5_6.3-2ubuntu0.3_amd64.deb
sudo apt install ./libtinfo5_6.3-2ubuntu0.3_amd64.deb
rm libtinfo5_6.3-2ubuntu0.3_amd64.deb
```

Si `wget` da 404, Ubuntu publicó un parche nuevo y borró el anterior: toma el `libtinfo5_6.3-2ubuntu0.*_amd64.deb` más alto de http://security.ubuntu.com/ubuntu/pool/universe/n/ncurses/ (el doctor con `--fix` ya lo resuelve solo).

Si no sabes si lo necesitas, puedes dejarlo para más adelante. No bloquea la instalación del driver NVIDIA.

Para **Ubuntu 24.04 LTS en equipos que van a correr MongoDB 8** (todas las estaciones de
compresión y de analítica), fija el kernel en el track **GA 6.8** antes de instalar cualquier
otro paquete. MongoDB 8 se niega a arrancar en kernels 6.19 – 7.0.13, que es lo que instala el
HWE de las ISO 24.04.4 en adelante:

```bash
sudo tee /etc/apt/preferences.d/99-no-hwe-kernel >/dev/null <<'EOF'
# MongoDB 8 vs kernel 6.19-7.0.13 (SERVER-121912): mantener track GA 6.8
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

Verifica que el pin apuntó al blanco correcto y **no** arrastró al track GA:

```bash
uname -r                                   # 6.8.0-1XX-generic si ya estás en GA
apt-cache policy linux-generic-hwe-24.04   # esperado: Candidate: (none), prioridad -1
apt-cache policy linux-image-generic       # esperado: 500 / 6.8.0-1XX.XXX  ← NO debe ser -1
```

> **Si `uname -r` ya muestra `7.0.0-XX`**, el equipo nació con el HWE instalado y este pinning
> solo evita que empeore: falta purgar el 7.0. No sigas con MongoDB; ve a la
> [Sección 14, Caso A](14-runbook-mongodb8-kernel.md#caso-a--equipo-ya-desplegado-corriendo-kernel-70).

> **Si `uname -r` muestra 6.9 – 6.18, no lo bajes a 6.8.** El techo de MongoDB 8 es 6.19: todo
> kernel anterior arranca `mongod` sin problema. El `6.11` de una ISO 24.04.2, el `6.14` de una
> 24.04.3 y el `6.14` que trae Linux Mint 22.2 ya son compatibles, y bajarlos a 6.8 resigna
> soporte de hardware sin arreglar nada. Aplicá el pinning igual: el HWE de noble hoy apunta a
> 7.0, así que sin pin el próximo `apt full-upgrade` sí rompe MongoDB. Y al purgar los
> metapaquetes HWE, marcá el kernel en uso como manual para que ningún `autoremove` lo saque:
>
> ```bash
> sudo apt-mark manual linux-image-$(uname -r) linux-modules-$(uname -r) \
>                      linux-modules-extra-$(uname -r) linux-headers-$(uname -r)
> ```
>
> El GA 6.8 queda instalado como track manejado (sigue recibiendo parches y es el respaldo para
> arrancar), y el equipo sigue usando el kernel que ya tenía. La contrapartida a saber: ese
> kernel queda congelado en su ABI actual, porque el metapaquete que lo hacía avanzar es
> justamente el que se bloquea.

## Paso 8: Verifica que la preparación quedó lista

Ejecuta:

```bash
gcc --version
dkms status
ls /usr/src/linux-headers-$(uname -r)
echo $XDG_SESSION_TYPE
```

Resultado esperado:

- `gcc --version` muestra una versión instalada.
- `dkms status` no muestra error, aunque puede no listar nada todavía.
- `ls /usr/src/linux-headers-$(uname -r)` muestra archivos del kernel.
- `echo $XDG_SESSION_TYPE` debería mostrar `x11` si estás en sesión gráfica.

## Si algo falla en la preparación

| Problema | Qué probar primero |
|----------|--------------------|
| `apt update` falla | Verifica internet con `ping -c 4 archive.ubuntu.com`. |
| No aparece Wi-Fi | Usa Ethernet o USB tethering temporal e instala `linux-firmware`; si es Broadcom, instala `bcmwl-kernel-source`. |
| No aparece Ethernet | Usa Wi-Fi, USB tethering o adaptador USB temporal; luego revisa el chip con `lspci -nn`. |
| No instala paquetes | Ejecuta `sudo apt --fix-broken install` y repite el comando. |
| Faltan headers del kernel | Ejecuta `sudo apt install -y linux-headers-$(uname -r) linux-headers-generic`. |
| `echo $XDG_SESSION_TYPE` muestra `wayland` | Revisa `/etc/gdm3/custom.conf`, confirma `WaylandEnable=false` y reinicia. |
| SSH no conecta | Revisa IP del equipo con `ip a` y estado del firewall con `sudo ufw status`. |
| No sabes si ya hay driver NVIDIA instalado | No sigas instalando encima. En la sección 4 se hará limpieza antes del `.run`. |

---

> [Índice](../README.md#índice) · [Anterior: 2. Instalación del Sistema Ubuntu](02-instalacion-ubuntu.md) · [Siguiente: 4. Instalación de Drivers de NVIDIA en Ubuntu](04-drivers-nvidia.md) · [English](en/03-system-preparation.md)
