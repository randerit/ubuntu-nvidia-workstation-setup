# 14. Runbook: MongoDB 8 no arranca por kernel HWE 7.0

> [Índice](../README.md#índice) · [Anterior: 13. Buenas Prácticas de Seguridad (Opcional)](13-seguridad.md) · [Siguiente: FAQ: Preguntas Frecuentes](15-faq.md) · [English](en/14-runbook-mongodb8-kernel.md)

> **Aplica a:** Ubuntu 24.04 LTS (noble) con `mongodb-org` 8.0.x.
> **Ticket upstream:** [SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912).
> **Estado:** mitigación vigente hasta que MongoDB libere el TCMalloc parcheado (ver *Criterio de salida*).
> **Validado en:** `equipo-de-pruebas`, 3 de Agosto de 2026.

Esta sección es un runbook: se aplica solo cuando el síntoma aparece (Caso A) o cuando se está
provisionando un equipo nuevo (Caso B). No es parte del flujo normal de instalación.

## Causa raíz

MongoDB 8.0+ empaqueta (vendoriza) una versión de TCMalloc que viola el ABI de **rseq**
(*restartable sequences*) del kernel. A partir de Linux 6.19 esto provoca crashes.

MongoDB agregó un guard explícito: **detecta kernels en el rango 6.19 – 7.0.13 y se niega a
arrancar**. Kernel 7.0.14 o superior resuelve la incompatibilidad.

El problema aparece en Ubuntu 24.04 porque Canonical rodó el stack **HWE de 26.04 (kernel 7.0)**
hacia noble. Las ISO 24.04.4 en adelante lo instalan por defecto en escritorio.

### Detalle crítico para Ubuntu

Ubuntu mantiene fijo el `X.Y.0-ABI` en `uname -r` y solo incrementa el número de ABI, aunque
internamente suba el sublevel upstream. Es decir: **cuando Canonical rebase a 7.0.14+, `uname -r`
seguirá reportando `7.0.0-XX`** y el guard de MongoDB seguirá bloqueando, incluso sobre un kernel
ya corregido.

**Conclusión operativa:** no esperes a que la próxima actualización HWE lo arregle. La salida es
quedarse en el track **GA 6.8**, que recibe parches de seguridad de Canonical hasta el fin de vida
de 24.04 y nunca salta de rama.

## Diagnóstico

```bash
uname -r                        # p.ej. 7.0.0-28-generic
cat /proc/version_signature     # base upstream REAL, p.ej. "... 7.0.12"
systemctl status mongod
journalctl -u mongod -b --no-pager | tail -30
```

Firma inequívoca del problema en el journal:

```
"s":"F","c":"CONTROL","id":12257600,"ctx":"main",
"msg":"MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility..."
```

`/proc/version_signature` distingue dos casos:

| Base upstream | Situación |
|---|---|
| ≤ 6.18 | Compatible: `mongod` arranca. No apliques este runbook; alcanza el pin del [Paso 7](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu). |
| 6.19 – 7.0.13 | Incompatibilidad real. Aplica este runbook. |
| ≥ 7.0.14 | Kernel ya corregido, pero el guard bloquea por el string de `uname`. Igual aplica este runbook. |

## Caso A — Equipo ya desplegado corriendo kernel 7.0

> **Orden obligatorio:** pinning → purge → verificar GRUB → reboot.
> Invertirlo deja ventanas donde apt reinstala el HWE, o donde el equipo arranca en 7.0 sin supervisión.

> **Con los paquetes `.deb` 2.4.0+ este runbook está automatizado**, respetando ese orden:
>
> ```bash
> sudo nvidia-cuda-setup --fix-kernel   # pin + gate de NIC + arranque unico en el GA
> sudo reboot
> sudo nvidia-cuda-setup --fix-kernel   # ya en el GA: purga los kernels bloqueados
> ```
>
> Deduce la fase de `uname -r`, se niega a fijar el arranque si el driver del GA no cubre la NIC
> (Caso C) y pide confirmación antes de purgar. Los pasos de abajo son la referencia de qué hace
> cada uno y qué verificar; también son la vía cuando el equipo no tiene los paquetes.

### Paso 1: Pinning y bloqueo (primero, siempre)

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

sudo apt update
```

Valida que el pinning apuntó al blanco correcto y **no** arrastró al track GA:

```bash
apt-cache policy linux-generic-hwe-24.04   # esperado: Candidate: (none), prioridad -1
apt-cache policy linux-image-generic       # esperado: 500 / 6.8.0-1XX.XXX  ← NO debe ser -1
```

### Paso 2: Asegura el track GA y quita los metapaquetes HWE

```bash
sudo apt install --install-recommends linux-generic
sudo apt purge linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 \
                linux-headers-generic-hwe-24.04
```

`apt install linux-generic` va **antes** del purge: así el metapaquete GA queda dueño de la
imagen 6.8 y ningún `autoremove` posterior puede dejarla huérfana.

> **Si el equipo corre 6.9 – 6.18 y `mongod` arranca**, terminá acá: no hace falta el Paso 3 ni
> el reinicio, porque el kernel en uso ya está debajo del techo. Antes del purge protegé su
> imagen, que al quedarse sin metapaquete pasa a ser automática:
>
> ```bash
> sudo apt-mark manual linux-image-$(uname -r) linux-modules-$(uname -r) \
>                      linux-modules-extra-$(uname -r) linux-headers-$(uname -r)
> ```

> **No intentes `apt-mark hold` sobre estos tres después del purge.** Falla:
>
> ```
> E: Can't select installed nor candidate version from package 'linux-generic-hwe-24.04' as it has neither of them
> ```
>
> No es un detalle de implementación, es estructural: la selección de dpkg es un **campo único**
> con valores `install` / `hold` / `deinstall` / `purge`. Un paquete purgado no puede estar además
> en `hold`, porque es el mismo slot. Y con el pin ya aplicado tampoco hay versión candidata que
> `apt-mark` pueda seleccionar.
>
> La protección real es el pin del Paso 1, que es **más fuerte** que un hold: deja
> `Candidate: (none)`, o sea que apt no puede instalarlos ni queriendo. Verificalo con
> `apt-cache policy linux-generic-hwe-24.04`.
>
> El `hold` sí sirve para paquetes que siguen instalados y querés congelar en su versión actual —
> por ejemplo `dkms`, ver *Cabos sueltos*.

### Paso 3: Arranca una vez en 6.8

```bash
sudo grub-reboot "Advanced options for Ubuntu>Ubuntu, with Linux 6.8.0-136-generic"
sudo reboot
```

> **Cuidado:** `grub-reboot` es **de un solo uso** (escribe `next_entry` en grubenv). No es la
> solución; es solo el puente para poder purgar el 7.0 sin tocar el kernel en ejecución. Ajusta
> `6.8.0-136-generic` a la versión que tengas: mírala con `ls /boot/vmlinuz-6.8.0-*`.

Tras el reboot:

```bash
uname -r                 # 6.8.0-1XX-generic
systemctl status mongod  # active (running)
dkms status              # módulos compilados para 6.8.0-1XX-generic
```

### Paso 4: Purga el kernel 7.0

**No uses globs a ciegas.** Un glob que no matchea nada hace que apt aborte la transacción
completa sin remover nada, y el mensaje de error pasa fácilmente por alto:

```
E: Couldn't find any package by glob 'linux-modules-extra-7.0.0-28*'
```

Enumera primero lo que realmente está instalado:

```bash
dpkg -l | awk '/^ii/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}'
```

Salida típica (6 paquetes):

```
linux-headers-7.0.0-28-generic
linux-hwe-7.0-headers-7.0.0-28
linux-hwe-7.0-tools-7.0.0-28
linux-image-7.0.0-28-generic
linux-modules-7.0.0-28-generic
linux-tools-7.0.0-28-generic
```

Purga esa lista y **revisa el resumen de apt antes de confirmar**: debe contener solo esos
paquetes. Si aparece algo con `6.8.0-1XX` o `nvidia-dkms-*`, cancela.

```bash
sudo apt purge $(dpkg -l | awk '/^ii/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}')
sudo apt autoremove --purge
sudo update-grub
```

DKMS desmontará el módulo NVIDIA del 7.0 en el proceso. Es esperado.

### Paso 5: Verificación previa al reboot (gate)

```bash
sudo update-grub                                       # debe listar solo el 6.8
ls /boot/vmlinuz-*                                     # una sola imagen
sudo grub-editenv list                                 # next_entry= vacío
dkms status                                            # solo 6.8.0-1XX-generic
dpkg -l | awk '/^(i|h)i/ && $2 ~ /^linux-.*7\.0\.0/ {print $2}'      # sin salida
sudo apt full-upgrade -s \
  | grep -E '^Inst (linux-image|linux-modules|linux-headers|linux-generic|linux-hwe)' \
  || echo "sin cambios de kernel"
```

`update-grub` no debe imprimir ninguna línea `Found linux image: /boot/vmlinuz-7.0.0-*`.

> **Dos detalles de los patrones, ambos vistos en terreno:**
>
> El último check **no** puede usar `grep -iE 'linux-|7\.0\.0'`: ese patrón engancha `linux-base`,
> `linux-firmware` y `linux-libc-dev`, que son paquetes normales y no kernels. Da falso positivo y
> te frena un equipo que está bien. El patrón de arriba solo mira líneas `Inst` de paquetes de
> kernel.
>
> El penúltimo usa `^(i|h)i` y no `^ii` porque **`apt-mark hold` cambia el estado en `dpkg -l` de
> `ii` a `hi`** (el primer carácter es la acción deseada, el segundo el estado real). Con `^ii` un
> paquete instalado pero en hold sale como ausente.

> **Nota:** `grep 'vmlinuz-7.0.0' /boot/grub/grub.cfg` da *Permission denied* porque `grub.cfg` es
> 0600 y el `sudo` no se propaga por el pipe. Usa la salida de `update-grub` o
> `sudo grep ... /boot/grub/grub.cfg`.

**Recién con todos estos checks en verde el equipo es seguro para reiniciar sin supervisión.**

### Paso 6: Limpia los overrides temporales de mongod

Si durante la mitigación se agregó un drop-in con `GLIBC_TUNABLES`, revísalo:

```bash
sudo systemctl cat mongod
```

- Un override con `glibc.pthread.rseq=0` es **redundante**: el unit de origen ya lo trae. Peor aún,
  cuando MongoDB cambie ese default al liberar el fix, el override lo pisará silenciosamente.
  Elimínalo.
- Un override con `glibc.pthread.rseq=1` era la mitigación de emergencia (hace que glibc gane el
  registro de rseq y TCMalloc caiga a cachés per-thread). En kernel 6.8 **sobra** y degrada el
  rendimiento al del allocator de MongoDB 7. Elimínalo.

```bash
sudo rm /etc/systemd/system/mongod.service.d/override.conf
sudo rmdir /etc/systemd/system/mongod.service.d
sudo systemctl daemon-reload && sudo systemctl restart mongod
systemctl cat mongod | grep -c override.conf   # esperado: 0
```

**Regla general:** nunca edites `/usr/lib/systemd/system/mongod.service` directamente — cualquier
upgrade de `mongodb-org-server` lo sobrescribe. Usa siempre `sudo systemctl edit mongod`.

## Caso B — Provisión de equipos nuevos

Mucho más corto, porque el 7.0 nunca llega a instalarse. Es el mismo pinning del
[Paso 7 de la Sección 3](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu). En `late-commands` del
autoinstall (o antes de sellar el golden image), **en este orden**:

1. Escribe `/etc/apt/preferences.d/99-no-hwe-kernel` y `/etc/apt/apt.conf.d/51-block-hwe-kernel`
   (contenido idéntico al Paso 1 del Caso A) — **antes de cualquier `apt install`**.
2. `apt-mark hold linux-generic-hwe-24.04 linux-image-generic-hwe-24.04 linux-headers-generic-hwe-24.04`
3. `apt install --install-recommends linux-generic`
4. Instala `mongodb-org` ([Sección 6](06-estaciones-compresion.md)).

Sin paso de GRUB, sin purge, sin reboot intermedio.

> El ISO de Ubuntu **Server** instala GA por defecto; el de **Desktop** instala HWE. Si despliegas
> desde Desktop, cada equipo nace con el problema.

## Caso C — Placas cuya NIC no funciona en el kernel GA

Aparece con placas madre nuevas: el puerto Ethernet levanta en el kernel HWE y muere al bajar al
GA 6.8. La salida obvia —instalar `linux-generic-hwe-24.04`, como sugiere la
[Sección 9](09-redes-placas-nuevas.md#9-solución-de-problemas-comunes-con-redes-en-placas-nuevas)— **está cerrada en toda
estación que corra MongoDB 8**, o sea en todas las de compresión y analítica.

Lo que hace falta no es un kernel más nuevo: es un **driver** más nuevo. El HWE es un atajo para
conseguirlo, no el único camino.

> **Regla de oro: necesitás red para arreglar la red.** Si pineás a GA, reiniciás y la NIC no
> levanta, quedás en un equipo sin red que no puede descargar el driver que lo arreglaría. El orden
> de esta sección existe para que eso no pase.

### Paso 1: Identificá el chip y su PCI ID, todavía con red

```bash
lspci -nn | grep -Ei 'ethernet|network'
```

Anotá el ID entre corchetes, formato `vendor:device` — por ejemplo `10ec:8125` (Realtek RTL8125) o
`8086:125c` (Intel I226-V). También el driver en uso:

```bash
for i in /sys/class/net/e*; do
  n=$(basename "$i")
  echo "$n -> $(basename "$(readlink -f "$i/device/driver")" 2>/dev/null)"
done
```

### Paso 2: Instalá el kernel GA sin reiniciar

Aplicá el pin del Caso A Paso 1, y después:

```bash
sudo apt install --install-recommends linux-generic
```

Esto trae los módulos del GA. Dónde vive cada driver, verificado sobre los paquetes 6.8.0-137:

| Paquete | Drivers Ethernet que contiene |
|---|---|
| `linux-modules-6.8.0-1XX-generic` | `e1000e`, `igb`, `ixgbe`, `i40e`, `8139too`… |
| `linux-modules-extra-6.8.0-1XX-generic` | **`r8169`**, **`igc`**, `atlantic`, y el resto |

Los dos que importan para este problema —`r8169` (Realtek) e `igc` (Intel I225/I226)— están en
`linux-modules-extra`. Llegan igual: `linux-image-generic` **depende** de él, no lo recomienda. Pero
si estás buscando el archivo a mano, está ahí y no en `linux-modules`.

### Paso 3: Preguntale al driver del GA si conoce tu placa

Todavía sin reiniciar:

```bash
# El kernel destino es el compatible (< 6.19) mas nuevo que haya instalado, no
# el 6.8 a secas: si el equipo ya tiene un 6.14, ahi va a arrancar.
KDEST=$(ls /lib/modules | awk -F. '$1 == 6 && $2 < 19' | sort -V | tail -1)
DRV=igc                  # o e1000e, igb, r8169 segun el Paso 1
ID=8086:125c             # el PCI ID del Paso 1

ALIAS="pci:v0000$(echo "${ID%:*}" | tr 'a-f' 'A-F')d0000$(echo "${ID#*:}" | tr 'a-f' 'A-F')"
modinfo -k "$KDEST" "$DRV" | grep -qi "$ALIAS" \
  && echo "OK: el driver de $KDEST conoce $ID" \
  || echo "FALTA: el driver de $KDEST no declara $ID"
```

`modinfo -k` consulta el módulo de **otro** kernel, así que funciona antes de arrancarlo. Requiere
que `linux-modules-extra-*` de ese kernel esté instalado, que es lo que hizo el Paso 2.

> **Este chequeo no sirve para las Realtek 2.5GbE.** El `r8169` del GA declara el alias con
> wildcard de revisión:
>
> ```
> alias: pci:v000010ECd00008125sv*sd*bc*sc*i*     (6.8.0-137, linux-modules-extra)
> ```
>
> Matchea las revisiones A, B, C y D, pero el código solo maneja hasta la C. Con un **RTL8125D**
> engancha el dispositivo y recién ahí se rinde:
>
> ```
> r8169 0000:07:00.0: unknown chip XID 688
> ```
>
> O sea que el comando de arriba imprime **OK** y la interfaz igual no levanta. Para `10ec:8125`
> saltá directo al Paso 4: no hay chequeo previo que lo descarte y el costo de instalar el driver
> de más es cero.

| Resultado | Camino |
|---|---|
| `10ec:8125` (cualquier revisión) | Paso 4 siempre, el alias no prueba nada |
| **OK** en el resto | El GA soporta la placa. Caso A normal desde el Paso 3 |
| **FALTA** | Paso 4 **antes** de reiniciar |

### Paso 4: Traé el driver por DKMS, con la red todavía viva

DKMS es la respuesta correcta porque **recompila el módulo en cada cambio de kernel**, así que
sobrevive los updates de la serie GA. `/etc/kernel/postinst.d/dkms` lo dispara al instalar un
kernel, y un mismo módulo queda construido para todos los kernels presentes.

**Realtek 2.5GbE (`10ec:8125`).** El `r8125-dkms` de los repos de Ubuntu **no alcanza**. noble trae
9.011.00, cuyo switch de detección de hardware cubre `0x60800000`, `0x64000000` y `0x64800000`
(CFG_METHOD_2 a 8) y manda cualquier otro al `default: unknown chip version`. El XID 688 es
`0x68800000`: cae ahí. El source no menciona el 8125D en ninguna parte — solo A, B y C.

Hace falta el driver del fabricante, **versión 9.014.01 o superior**, empaquetado para DKMS:

```bash
sudo apt install -y dkms build-essential "linux-headers-$GA"

# Si quedó instalado el de Ubuntu, sacarlo: dos módulos reclamando 10ec:8125
sudo apt purge -y r8125-dkms

VER=9.016.01-1
wget "https://github.com/awesometic/realtek-r8125-dkms/releases/download/${VER}/realtek-r8125-dkms_${VER}_amd64.deb"
sudo dpkg -i "realtek-r8125-dkms_${VER}_amd64.deb"
```

El `postinst` compila para el kernel **corriendo** (el HWE), y ese build puede fallar contra las
APIs de un kernel nuevo. No importa: en el HWE el `r8169` in-tree ya maneja el 8125D. Lo único
crítico es que quede compilado para el GA, y eso se fuerza aparte:

```bash
sudo dkms install realtek-r8125/9.016.01 -k "$GA" --force
```

> **No blacklistees `r8169`.** El paquete del fabricante a veces lo deja hecho, y eso mata las
> RTL8168/8111 (`10ec:8168`), que dependen de él —en placas con dos puertos suele ser el único
> enlace que funciona. No hace falta, y el mecanismo real no es el orden de `depmod`: los dos
> módulos declaran el alias del `10ec:8125`, `modprobe` carga los dos y el device se lo queda el
> primero cuyo probe funcione. El `r8169` viene en el initramfs y llega antes —medido en terreno,
> `r8169` a los 0.8 s y `r8125` a los 3.4 s—, así que se queda con las revisiones que soporta y el
> `r8125` queda cargado sin usar, inofensivo. Con el 8125D falla el probe, libera el device y ahí lo
> toma el `r8125`.
>
> **Por eso la verificación es por driver bindeado, no por módulo cargado:**
>
> ```bash
> ethtool -i enp5s0 | head -2      # driver: r8125 si el r8169 rechazó la placa
> lsmod | grep -E 'r8169|r8125'    # los dos pueden estar cargados: no prueba nada
> ```
>
> ```bash
> grep -rl 'blacklist[[:space:]]\+r8169' /etc/modprobe.d/   # si devuelve algo, borrá esa linea
> ```

**Intel `igc` (I225/I226).** No hay paquete DKMS en los repos: hay que compilar del source que
publica Intel en su Download Center y envolverlo en DKMS. Más trabajo, y por eso las dos
alternativas de hardware suelen ganar en tiempo:

- **NIC PCIe Intel I210 o I350.** Sólida en GA 6.8, cero DKMS que mantener. Es la opción más barata
  medida en horas de operación.
- **Adaptador USB Ethernet.** Inmediato. Verificá que soporte Wake-on-LAN si esa estación lo
  necesita, porque muchos no lo hacen.

Si no hay red en absoluto para descargar el DKMS, usá tethering USB desde un teléfono o llevá el
`.deb` y sus dependencias en un pendrive.

> Si estás aprovisionando con los `.deb` del proyecto, todo este paso lo hace `nic-driver-rescue`,
> que viaja dentro de `nvidia-cuda-setup`, `workstation-compression` y `workstation-analytics`. Detecta la NIC, saca
> el `r8125-dkms` viejo, baja el del fabricante, compila para el GA, quita el blacklist y verifica.
> Con `--deb RUTA` o `--no-download` funciona sin internet.

### Paso 5: Verificá que el módulo quedó construido para el GA

**Antes de reiniciar**, y esto es lo que decide si es seguro hacerlo. `dkms status` es el primer
paso pero no basta:

```bash
dkms status
sudo dkms autoinstall     # si no lista el modulo para el GA
```

Lo que realmente carga el driver al arrancar es `udev` consultando `modules.alias`. Verificá el
archivo, **su versión** y el índice, en ese orden:

```bash
sudo depmod -a "$GA"

# 1. El .ko existe, y esta en updates/ (que es lo que le gana al in-tree)
KO=$(find "/lib/modules/$GA/updates" -name 'r8125.ko*' -print -quit)
echo "${KO:-NO HAY MODULO}"

# 2. Y es del fabricante, no el 9.011.00 de noble
modinfo -F version "$KO"          # tiene que ser >= 9.014.01

# 3. udev lo va a encontrar por el alias
awk '$1=="alias" && index($2,"pci:v000010ECd00008125")==1 {print $3}' \
    "/lib/modules/$GA/modules.alias"
```

El primero tiene que devolver una ruta, el segundo una versión **9.014.01 o superior**, y el tercero
tiene que incluir `r8125`. Si el `find` vuelve vacío, **no reinicies**: el equipo queda sin red.

> **El paso 2 no es opcional, y durante un tiempo faltó en esta guía.** El `r8125-dkms` 9.011.00 de
> los repos de noble también deja un `r8125.ko` en `updates/dkms/`, así que el `find` del paso 1
> devuelve una ruta y todo parece en orden — pero ese driver manda el XID 688 a
> `unknown chip version` igual. Es el **falso verde** más caro de este runbook: pasa el chequeo,
> reiniciás, y la placa rev D queda sin red. Si la versión es menor a 9.014.01, tratalo como
> **FALTA** y volvé al Paso 4.

> No uses `modinfo -k "$GA" r8125` para esto. En árboles `/lib/modules` creados solo por DKMS, sin
> paquete de kernel, `modinfo` por nombre da falsos negativos. Verificá por archivo.

### Paso 6: Recién ahora, arrancá en el GA

Usá un arranque **one-shot** en vez de cambiar el default. Si la red no levanta, el siguiente
reinicio vuelve solo al kernel anterior y no perdés el acceso:

```bash
sudo grub-reboot "Advanced options for Ubuntu>Ubuntu, with Linux $GA"
sudo reboot
```

Ya arriba, agregá la red al gate del Caso A Paso 5, antes de purgar el kernel viejo:

```bash
ip -br link show                 # la interfaz Ethernet en estado UP
ethtool -i enp5s0 | head -2      # QUE driver quedo bindeado, no cual esta cargado
ping -c 3 archive.ubuntu.com
```

Con la red validada, recién ahí fijá el GA como default permanente:

```bash
sudo sed -i "s|^GRUB_DEFAULT=.*|GRUB_DEFAULT=\"Advanced options for Ubuntu>Ubuntu, with Linux $GA\"|" /etc/default/grub
sudo update-grub
```

**No purgues el kernel HWE hasta que la red funcione en el GA.** Mientras siga instalado tenés un
arranque de rescate; el pin impide que se reinstale, pero no borra lo que ya está.

## Preflight de Ansible para la flota

Agrega esto como primera tarea de los plays de la flota, para que un equipo mal aprovisionado falle
ruidosamente en consola en vez de romperse en silencio en terreno:

```yaml
- name: Kernel incompatible con MongoDB 8 (SERVER-121912)
  ansible.builtin.assert:
    that:
      - ansible_kernel is version('6.19', '<')
    fail_msg: >-
      {{ inventory_hostname }} corre {{ ansible_kernel }}: el rango 6.19-7.0.13
      bloquea el arranque de mongod. Aplicar el runbook (Caso A) antes de continuar.
    success_msg: "Kernel {{ ansible_kernel }} OK para MongoDB 8"
```

En equipos sueltos, el mismo control lo hacen los scripts doctor de la
[Sección 12](12-scripts-doctor.md#12-scripts-doctor-de-verificación) con el check *Kernel compatible con MongoDB 8*.

## Cabos sueltos

- **THP:** MongoDB 8.0 requiere Transparent Huge Pages **habilitado** — al revés que 7.0 y
  anteriores. Si algún script de provisión antiguo arrastra `transparent_hugepage=never` en
  `GRUB_CMDLINE_LINUX` o una unit de systemd que lo desactiva, quítalo.
- **`GRUB_DEFAULT` numérico:** no uses índices (`"1>2"`). Se desplazan con cada kernel instalado y
  el equipo termina arrancando otra cosa semanas después. Con el 7.0 purgado, GRUB elige el 6.8 solo
  y no hace falta fijar nada.
- **dkms de terceros:** en `equipo-de-pruebas` el paquete `dkms` viene del repo local de CUDA
  (`dkms/unknown 1:3.2.1-1ubuntu2`) en vez del de noble. Mezclar versiones puede complicar la
  recompilación de módulos NVIDIA en el próximo cambio de kernel. Si los módulos no recompilan, es
  el primer sospechoso. Evalúa `apt install dkms=3.0.11-1ubuntu13` + hold, salvo que CUDA 13 lo
  exija.

## Criterio de salida (cuándo revertir esto)

Este runbook es una mitigación, no un estado final. Revisa periódicamente
[SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912).

Condiciones para volver a abrir el carril HWE:

1. MongoDB publica una release con TCMalloc parcheado y lo confirma en las release notes /
   production notes (hoy solo dicen que se resolverá "as soon as a patched version of TCMalloc is
   available").
2. Validar en **un** equipo de laboratorio: instalar el HWE, verificar `/proc/version_signature`,
   confirmar que `mongod` arranca **y sigue vivo pasados varios minutos** (hubo un modo de falla con
   SIGSEGV a los 30-60 s por Shadow Stacks / CET en CPUs Zen 5, distinto del bug de rseq).
3. Recién entonces: quitar el pinning, los holds y la blacklist de unattended-upgrades, el check de
   los scripts doctor, y actualizar esta sección.

## Troubleshooting

- **`apt purge` aborta con `Couldn't find any package by glob ...`:** No removió nada. Enumera con
  el `dpkg -l | awk ...` del Paso 4 y purga la lista real.
- **`apt-cache policy linux-image-generic` muestra `-1`:** El pin se pasó de ancho y bloqueó el
  track GA. Revisa la línea `Package:` de `/etc/apt/preferences.d/99-no-hwe-kernel`.
- **Tras el reboot el equipo volvió al 7.0:** `grub-reboot` es de un solo uso. Repite el Paso 3 y
  no reinicies de nuevo hasta terminar los Pasos 4 y 5.
- **Los módulos NVIDIA no recompilan en el 6.8:** `sudo dkms autoinstall && dkms status`. Si sigue
  fallando, revisa la versión de `dkms` (ver *Cabos sueltos*) y reinstala el driver `.run` de la
  [Sección 4](04-drivers-nvidia.md#4-instalación-de-drivers-de-nvidia-en-ubuntu).
- **`mongod` arranca y muere a los 30-60 s con SIGSEGV:** No es este bug. Es Shadow Stacks / CET en
  CPUs Zen 5, un modo de falla distinto.

---

> [Índice](../README.md#índice) · [Anterior: 13. Buenas Prácticas de Seguridad (Opcional)](13-seguridad.md) · [Siguiente: FAQ: Preguntas Frecuentes](15-faq.md) · [English](en/14-runbook-mongodb8-kernel.md)
