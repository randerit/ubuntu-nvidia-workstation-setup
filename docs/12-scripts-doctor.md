# 12. Scripts Doctor de Verificación

> [Índice](../README.md#índice) · [Anterior: 11. Script de Post-Instalación (Opcional)](11-script-post-instalacion.md) · [Siguiente: 13. Buenas Prácticas de Seguridad (Opcional)](13-seguridad.md) · [English](en/12-doctor-scripts.md)

> **Nota:** Los scripts doctor permiten verificar que todos los componentes de una estación estén instalados correctamente y, opcionalmente, instalar los faltantes de forma automática. Existen tres variantes según el tipo de estación.

> Los scripts viven en [`scripts/`](../scripts/) y los comandos de esta sección se ejecutan desde la raíz del repositorio. Si copias los scripts a otro equipo, copia la carpeta `scripts/` completa: las librerías (`doctor_lib.sh`, `nic_lib.sh`) se buscan junto a cada script.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| [`doctor_lib.sh`](../scripts/doctor_lib.sh) | Librería compartida con funciones de verificación, instalación y resumen. No se ejecuta directamente. |
| [`doctor_compresion.sh`](../scripts/doctor_compresion.sh) | Verifica e instala componentes para estaciones de **compresión** (secciones 3-6). |
| [`doctor_analitica.sh`](../scripts/doctor_analitica.sh) | Verifica e instala componentes para estaciones de **analítica** (secciones 3-5 y 7). |
| [`doctor_visualizacion.sh`](../scripts/doctor_visualizacion.sh) | Verifica e instala componentes para estaciones de **visualización** (secciones 3-6, sin el stack de video). |
| [`self_check_doctor_lib.sh`](../scripts/self_check_doctor_lib.sh) | Prueba los chequeos de red de `doctor_lib.sh` contra árboles falsos en un tmpdir. No toca el sistema; sirve para validar cambios en la librería antes de llevarla a un equipo. |
| [`nic_lib.sh`](../scripts/nic_lib.sh) | Librería compartida con el conocimiento canónico de las Realtek 2.5GbE: revisiones/XID, versión mínima del driver, validación del `.ko` y las dos reglas de diagnóstico (driver y chip colgado). No se ejecuta directamente. |
| [`diag-nic.sh`](../scripts/diag-nic.sh) | Diagnóstico por capas de **un puerto** de red. Solo lee y captura; no cambia configuración. |
| [`fix-r8125-downgrade-6.8.sh`](../scripts/fix-r8125-downgrade-6.8.sh) | Remediación: prepara el driver y el kernel GA 6.8, verifica, y recién entonces arma el arranque one-shot. **Sí** modifica el sistema. |
| [`self_check_nic_lib.sh`](../scripts/self_check_nic_lib.sh) | Prueba `nic_lib.sh` y las reglas de `diag-nic.sh` contra los escenarios A–I de terreno. Sin root, sin hardware, sin red. |

> **Desde la versión 2.3.0 los doctor verifican la red del Caso C**, junto al pin del kernel en la
> sección de MongoDB: que cada NIC Ethernet del bus PCI tenga driver activo —el fallo del RTL8125D
> se ve en sysfs y no necesita cable—, que todo módulo DKMS tenga build para el kernel en ejecución
> (un `r8125` construido solo para el kernel anterior deja el equipo sin red en el próximo reinicio)
> y que nadie haya dejado un `blacklist r8169`, que mata las RTL8168/8111.


## Diagnóstico y remediación de red (`diag-nic.sh` y `fix-r8125-downgrade-6.8.sh`)

Los dos son parte del [Caso C de la Sección 14](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga)
y comparten `nic_lib.sh`. **Copiá el repo completo al equipo**, no los archivos sueltos: sin
`nic_lib.sh` al lado no arrancan (y lo dicen).

### Dos caminos, un solo fuente

Estos scripts —y los tres doctor— viajan **también dentro de los `.deb` del proyecto**, copiados byte
a byte desde este repo al construirlos. No hay dos versiones que mantener: el build de
`Ubuntu-NVIDIA-Deb-Packages` los toma de acá, y su suite verifica el sha256 de cada uno contra el
original.

| | Archivos sueltos de este repo | Dentro del `.deb` |
|---|---|---|
| Para qué | **Terreno**: resolver un conflicto en un equipo que ya está desplegado | **Oficina**: aprovisionar equipos que salen a terreno |
| Cómo llegan | `scp` del repo, o pendrive | Ya instalados con el paquete |
| Se invocan | `./scripts/diag-nic.sh`, `./scripts/doctor_compresion.sh` | `nic-diag`, `workstation-doctor-compresion`, `nic-kernel-downgrade`, `workstation-doctor-analitica` |
| Dónde viven | El directorio donde los copiaste | `/usr/local/lib/workstation-tools/`, con wrappers en `/usr/local/bin/` |

Y el instalador de perfil **cierra corriendo su doctor** (modo lectura, sin `--fix`), así que
aprovisionar y verificar es un solo comando:

```bash
sudo workstation-dependencies --perfil compresion       # primera vez: instala y termina con el doctor
sudo workstation-dependencies --no-doctor               # reinstalar/reejecutar sin verificar
workstation-dependencies --doctor-only                  # verificar sin instalar
```

`--doctor-only` es el modo gate: no instala nada, **no necesita root** (el doctor en modo lectura no
toca el sistema) y **sale con el número de fallos como exit code**, así que sirve para decidir si un
equipo se despacha o no:

```bash
if workstation-dependencies --doctor-only; then
  echo "listo para terreno"
fi
```

Al terminar una instalación es al revés: ahí el doctor informa y **no** cambia el exit code del
instalador, porque la instalación hizo lo que podía hacer.

> **`nic-kernel-downgrade` (o sea, `fix-r8125-downgrade-6.8.sh`) no lo invoca nadie
> automáticamente.** El pin del kernel, el gate de NIC y el `grub-reboot` del aprovisionamiento ya
> los hace `nvidia-cuda-setup --fix-kernel` con `nic-driver-rescue`. Este script existe para el
> equipo que **ya está en terreno** y necesita además el hardening ASPM/EEE, el watchdog de
> auto-sanación y la persistencia netplan por MAC. Detecta el pin del instalador y no escribe un
> segundo archivo, así que correrlo después es seguro; lo que no tiene sentido es alternarlos.

### `diag-nic.sh` — solo lectura

```bash
sudo ./scripts/diag-nic.sh <interfaz> [segundos_de_captura] [gateway_de_prueba]
sudo ./scripts/diag-nic.sh enp13s0 30 192.0.2.1
```

`192.0.2.1` es una IP de documentación (RFC 5737): reemplázala por el gateway o un servidor alcanzable de tu red.

Deja tres artefactos en el directorio actual: el log completo, un `.pcap` de la captura sin filtro y
una línea en `diag-results.csv` para consolidar varios equipos.

El resumen **no** mezcla observaciones con causas. Cada hallazgo cae en un bloque y una severidad:

| Bloque | Responde |
|---|---|
| `SALUD ACTUAL DEL LINK` | ¿La NIC está funcionando ahora? |
| `DRIVER / HARDWARE` | ¿El driver bindeado es el correcto para este chip y este kernel? |
| `DHCP / L3` | ¿Hay IP y alcance? |
| `PERSISTENCIA TRAS REBOOT` | ¿Esto sobrevive al próximo reinicio? |
| `RIESGOS DE CONFIGURACIÓN` | Buenas prácticas pendientes y pistas del lado del switch |

| Severidad | Significa |
|---|---|
| `[INFO]` | Observación. Nada que hacer |
| `[AVISO]` | Riesgo o buena práctica pendiente. **No** es una falla actual |
| `[SOSPECHA]` | Compatible con una falla, pero falta evidencia para afirmarla |
| `[FALLO]` | Confirmado con la evidencia disponible |

Códigos de salida, para consolidar flota: `0` sin hallazgos, `1` avisos, `2` sospechas, `3` fallos.

**Dos cosas que este script no hace, a propósito.** No marca `r8169` como driver incorrecto por sí
solo: la regla mira kernel, PCI ID, XID y el driver realmente bindeado en sysfs
(`readlink -f /sys/class/net/<iface>/device/driver`, equivalente a `ethtool -i`), nunca `lsmod`. Y no
declara un chip "colgado" porque `rx_packets` no se movió unos segundos: combina RX e interrupciones
sobre una ventana larga (≥ 30 s), la captura sin filtro y un `NETDEV WATCHDOG` **reciente y fechado**,
y sale con uno de cuatro niveles —`NORMAL`, `SOSPECHOSO`, `PROBABLE`, `MUY_FUERTE`—. Si la captura vio
tráfico, el chip recibe y no puede pasar de `SOSPECHOSO` por más señales que se acumulen.

La **Capa 8** es la que importa antes de un downgrade remoto: si la placa tiene un `10ec:8125` y el
equipo todavía no corre el GA, verifica que exista un `r8125.ko` **de versión suficiente** para el
kernel 6.8 destino y que esté indexado en `modules.alias`. Si falta, el resumen dice
`NO REINICIAR al kernel GA todavía`.

### `fix-r8125-downgrade-6.8.sh` — modifica el sistema

```bash
sudo ./scripts/fix-r8125-downgrade-6.8.sh --dry-run    # ver qué haría
sudo ./scripts/fix-r8125-downgrade-6.8.sh
```

Ejecuta, en este orden y sobre el kernel viejo **con la red todavía viva**: comprobación de
conectividad, análisis del NIC y compilación del `r8125` contra los headers 6.8, hardening ASPM/EEE,
instalación del kernel GA con pin y hold, watchdog de auto-sanación, persistencia de red por MAC, y
recién al final un **gate de pre-reboot** que imprime un checklist auditable:

```
imagen del kernel · initramfs · paquetes configurados (incluido modules-extra) ·
entrada de GRUB · pin de apt · sin blacklist de r8169 ·
r8125.ko presente, de versión suficiente, válido para modinfo, con depmod hecho
y alias PCI indexado
```

Si falta algo crítico imprime **`NO REINICIAR`**, no arma el arranque one-shot y sale con `1`. Solo
cuando el checklist está completo ejecuta `grub-reboot` y dice `SEGURO REINICIAR`. Ese orden es
deliberado: el equipo nunca queda apuntando a un kernel que no puede levantar la red.

### Reejecutar es barato: comprobar antes de actuar

Los dos scripts se reejecutan seguido —una fase falla, se corrige algo, se vuelve a correr— así que
**ningún paso rehace trabajo ya hecho**. `fix-r8125-downgrade-6.8.sh` escribe cada archivo de
configuración solo si el contenido difiere del que ya está en disco, y de ahí cuelgan las
operaciones caras:

| Archivo | Qué se evita al reejecutar |
|---|---|
| `/etc/modprobe.d/nic-r8125-options.conf` | `update-initramfs -u -k` (~30 s) |
| `/etc/udev/rules.d/90-nic-r8125-override-*.rules` | `udevadm control --reload-rules` |
| `r8125-zombie-watchdog.sh`, `.service`, `.timer` | `systemctl daemon-reload` |
| `/etc/apt/preferences.d/99-workstation-pin-ga-kernel` | reescritura del pin |

Y los pasos que ya estaban comprobados siguen igual: no recompila el `r8125` si ya hay uno válido
para el kernel objetivo, no reinstala el kernel GA si los paquetes están bien configurados, y no
escribe un segundo pin si ya está el del instalador. `systemctl enable --now` del watchdog sí corre
siempre, a propósito: es idempotente y barato, y repara un timer que alguien haya deshabilitado.

`diag-nic.sh` no aplica: solo lee y captura.

> **Correr `./scripts/self_check_nic_lib.sh` después de tocar cualquiera de estos tres archivos.** Cubre los
> escenarios de terreno A–I (r8169 legítimo en 6.8, RTL8125D real, kernel 7.x, red silenciosa,
> zombie con evidencia fuerte, sin carrier, DHCP sin Offer, perfil efímero, XID indeterminable) sin
> tocar el sistema.

## Uso Básico

### Solo verificar (sin instalar nada)
```bash
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh      # Para estaciones de compresión
./scripts/doctor_analitica.sh       # Para estaciones de analítica
./scripts/doctor_visualizacion.sh   # Para estaciones de visualización
```

### Verificar e instalar faltantes automáticamente
```bash
./scripts/doctor_compresion.sh --fix
./scripts/doctor_analitica.sh --fix
./scripts/doctor_visualizacion.sh --fix
```

Con `--fix` el script:
1. Solicita `sudo` una sola vez al inicio.
2. Ejecuta `apt update` una sola vez.
3. Para cada check que falla, intenta instalar el componente y re-verifica.
4. Genera un log completo en `/tmp/doctor_fix_YYYYMMDD_HHMMSS.log`.

## Flujo Recomendado

```
1. Ejecutar el script sin --fix para diagnosticar
             │
             ▼
2. ¿Hay fallos en NVIDIA Driver o CUDA?
   ├─ SÍ → Instalar manualmente (secciones 4 y 5 de esta guía)
   └─ NO → Continuar
             │
             ▼
3. Ejecutar con --fix para instalar el resto automáticamente
             │
             ▼
4. Verificar resumen final
   ├─ Todo OK → Listo
   └─ Aún hay fallos → Revisar /tmp/doctor_fix_*.log
```

> **Importante:** Los drivers NVIDIA y CUDA Toolkit requieren instalación manual (reboot, modo texto, configuración de PATH). El script los detecta pero no los instala automáticamente; en su lugar muestra instrucciones para seguir las secciones correspondientes de esta guía.

## Niveles de Severidad

Los scripts clasifican los resultados en distintos niveles para facilitar la priorización:

| Tag | Nivel | Descripción | Ejemplo |
|-----|-------|-------------|---------|
| `[OK]` | Correcto | Componente instalado y funcionando | build-essential, nvidia-smi, MongoDB |
| `[FALLO]` | Crítico | Componente esencial faltante | Paquetes del sistema, drivers, CUDA |
| `[AVISO]` | Aviso crítico | Componente opcional importante ausente | Servicios no iniciados, herramientas remotas |
| `[NOTA]` | Menor | Configuración opcional no aplicada | Puertos de firewall no configurados |
| `[INFO]` | Informativo | Datos del sistema detectados | Versión de GPU, kernel, IP |

En el resumen:
- **SALUDABLE:** 0 fallos y 0 avisos. Las notas menores no afectan el estado.
- **SALUDABLE CON AVISOS:** 0 fallos, pero hay avisos críticos pendientes.
- **ATENCIÓN REQUERIDA:** 1-3 fallos.
- **REQUIERE INTERVENCIÓN:** Más de 3 fallos.

## Qué Verifica Cada Script

### Componentes comunes (ambos scripts)
- Sistema operativo (Ubuntu, kernel, arquitectura)
- Dependencias de desarrollo (build-essential, dkms, GCC, librerías OpenGL/Mesa/GStreamer)
- Herramientas de calidad de vida (git, curl, wget, vim, htop, ncdu, nmap, etc.)
- Entorno gráfico (Xorg vs Wayland)
- SSH y firewall
- Dependencias de desarrollo: headers del kernel en ejecución, necesarios para que DKMS recompile el módulo NVIDIA
- Drivers NVIDIA (nvidia-smi, módulos kernel, detección GPU)
- Driver en la rama fijada por el manual (580.x.x) e instalado por `.run` y **no** por APT. Un equipo con `nvidia-driver-*` de APT pasaba todos los checks NVIDIA aunque la [Sección 4](04-drivers-nvidia.md) lo trate como error a purgar
- Módulo open/MIT-GPL, recomendado por la [Sección 4](04-drivers-nvidia.md) Paso 5 para RTX 20/30/40/50
- CUDA Toolkit (nvcc, PATH, LD_LIBRARY_PATH, configuración en sistema)
- CUDA coherente: `nvcc`, el symlink `/usr/local/cuda` y `dpkg` apuntando todos a la misma versión. El número en sí es informativo — la [Sección 5](05-cuda-toolkit.md) fija 13.0, pero un equipo que llegó con 13.1 o 13.4 es válido mientras no haya desacuerdo entre las fuentes
- Pin del kernel GA persistente. Verificar solo `uname -r` no alcanza: un equipo hoy en 6.8 pero sin pin vuelve al HWE en el próximo `apt upgrade` y se queda sin base de datos
- Transparent Huge Pages habilitado, que MongoDB 8.0 requiere

### Solo compresión (`doctor_compresion.sh`)
- MongoDB y MongoDB Compass, incluyendo kernel compatible con MongoDB 8 (falla si está en el rango 6.19 – 7.0.13, ver [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70))
- EMQX (broker MQTT)
- Golang y Visual Studio Code
- GStreamer y todos sus plugins (base, good, bad, ugly, libav, RTSP, NVIDIA, etc.)
- Herramientas remotas (Angry IP Scanner, AnyDesk, RustDesk)
- Override de systemd de AnyDesk, que el Paso 2 de la [Sección 6](06-estaciones-compresion.md) declara obligatorio. Sin él AnyDesk crashea y congela GNOME, y el paquete instalado a secas no lo delata
- Puertos: 27017 (MongoDB), 1883 (MQTT), 18083 (EMQX Dashboard)

### Solo analítica (`doctor_analitica.sh`)
- MongoDB con verificación de autorización y de kernel compatible con MongoDB 8 (falla si está en el rango 6.19 – 7.0.13, ver [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70))
- Node-RED, Node.js y npm
- Python 3, pip3 y bibliotecas ML (pandas, numpy, scikit-learn, paho-mqtt, ultralytics)
- Puertos: 27017 (MongoDB), 1880 (Node-RED)

### Solo visualización (`doctor_visualizacion.sh`)
- Estación que abre las interfaces web y mira el software; lleva herramientas de desarrollo por si hacen falta en el sitio
- MongoDB y MongoDB Compass (sin autorización), EMQX, MQTTX, Docker, ffmpeg, AnyDesk con su override X11, Golang y Visual Studio Code
- Sin GStreamer (runtime), RustDesk, Angry IP, stack ML ni Node-RED
- Acepta `--skip-mongodb`, `--skip-emqx` y `--skip-snaps`: lo omitido se informa como `[INFO]`, no como `[FALLO]`; tampoco se verifican (ni se abren con `--fix`) los puertos de lo omitido: 27017 con `--skip-mongodb`, 1883 y 18083 con `--skip-emqx`
- Puertos: 22 (SSH), 27017 (MongoDB), 1883 y 18083 (EMQX), AnyDesk (80, 443, 6568, 50001-50003/udp); sin RTSP 554 ni Node-RED 1880

## Troubleshooting
- **El script falla al iniciar:** Verifica que `doctor_lib.sh` esté en el mismo directorio.
- **"UFW no activo, omitiendo verificación de puertos":** ufw 0.36 (Ubuntu 22.04/24.04) no carga sus traducciones, así que su salida hoy es en inglés. Los doctores igual la leen con `LANGUAGE=C LC_ALL=C` (`LANGUAGE=C LC_ALL=C sudo ufw status`), para que una versión de ufw que sí traduzca (`Estado: activo`) no rompa la detección, y solo la línea `Status: active` cuenta como activo. `Status: inactive` omite la verificación de puertos; activa UFW ([Sección 3](03-preparacion-del-sistema.md)) para que se verifiquen.
- **"[AVISO] No se pudo leer el estado de UFW":** `ufw` está instalado pero `sudo ufw status` falló (tu usuario no tiene permiso de sudo para `ufw`, o sudo pidió contraseña), así que no se sabe si el firewall está activo y los puertos quedan sin verificar. Corre `sudo ufw status` a mano para ver el error. Es un aviso y no cambia el exit code.
- **`--fix` no instala algo:** Revisa el log en `/tmp/doctor_fix_*.log` para ver el error exacto.
- **Paquete Python no detectado:** El script usa `pip3 show` para verificar, que es más robusto que `import`. Si falla, verifica con `pip3 list | grep <paquete>`.
- **NVIDIA módulo no detectado:** El script verifica vía `lsmod`, `/proc/driver/nvidia/version` y `nvidia-smi` como fallback. Si todo falla, revisa que el driver esté instalado correctamente.
- **CUDA no detectado:** El script busca `nvcc` en `/usr/local/cuda*/bin/` y también verifica configuración en `~/.bashrc`, `/etc/profile.d/` y `/etc/environment`.
- **"Kernel compatible con MongoDB 8" falla:** No tiene autofix; `--fix` no puede cambiar el kernel en ejecución. Aplica la [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70) a mano y vuelve a correr el script.
- **"Driver instalado por .run y no por APT" falla:** Hay paquetes `nvidia-*` de APT. No tiene autofix a propósito: purgar el driver activo requiere modo texto. Aplica los pasos 3 a 6 de la [Sección 4](04-drivers-nvidia.md#4-instalación-de-drivers-de-nvidia-en-ubuntu).
- **"Pin del kernel GA persistente" falla:** Falta `/etc/apt/preferences.d/99-no-hwe-kernel` o `/etc/apt/apt.conf.d/51-block-hwe-kernel`, o el pin no dejó `Candidate: (none)`. Aplica el [Paso 7 de la Sección 3](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu). Este check puede dar verde en `uname -r` y rojo acá: significa que el equipo está bien hoy y roto en el próximo `apt upgrade`.
- **"Driver en la rama 580.x.x" falla:** El manual fija esa familia. Cambiar de rama solo con razón concreta: GPU nueva, bug crítico corregido o validación interna. Ver [Anexo B](17-anexo-b-compatibilidad.md#anexo-b-verificación-de-compatibilidad).
- **"AnyDesk con override X11" falla:** `--fix` lo aplica escribiendo el override y reiniciando el servicio. También lo hace al instalar AnyDesk desde cero.
- **Un paquete instalado aparece como ausente:** Si está en `hold`, `dpkg -l` lo muestra como `hi` y no `ii`. Los scripts usan `pkg_installed`, que consulta `dpkg-query` y no se confunde; si escribís un check propio, no uses `grep '^ii'`.

---

> [Índice](../README.md#índice) · [Anterior: 11. Script de Post-Instalación (Opcional)](11-script-post-instalacion.md) · [Siguiente: 13. Buenas Prácticas de Seguridad (Opcional)](13-seguridad.md) · [English](en/12-doctor-scripts.md)
