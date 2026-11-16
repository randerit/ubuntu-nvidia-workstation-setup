# Anexo C: Matriz de Compatibilidad de Kernel (Ubuntu 24.04 LTS)

> [Índice](../README.md#índice) · [Anterior: Anexo B: Verificación de Compatibilidad](17-anexo-b-compatibilidad.md) · [English](en/18-annex-c-kernel-matrix.md)

> **Para qué sirve este anexo.** La pregunta operativa no es "¿qué versión de cada paquete uso?" sino
> "¿cuál de estos componentes se rompe si el kernel se mueve?". Son tres. Todo el resto de la
> instalación es userspace sobre la glibc 2.39 de noble y no cambia con la serie del kernel. La bola
> de nieve no la arman las versiones de los paquetes: la arma mezclar tracks de kernel.
>
> Datos verificados contra Launchpad, el repositorio de MongoDB y kernel.org el **21 de agosto de 2026**.

## C.1 Series de kernel disponibles para 24.04

| Serie | De dónde viene | Última publicada para noble | Soporte | MongoDB 8 |
|-------|----------------|-----------------------------|---------|-----------|
| **6.8 GA** | Kernel propio de 24.04 | `6.8.0-138` (updates/security), `6.8.0-139` en proposed | **Abril 2029** estándar, ESM Pro hasta 2034 | ✅ |
| 6.11 | HWE de 24.10 | `6.11.0-29` | Serie superada | ✅ arranca |
| 6.14 | HWE de 25.04 | `6.14.0-37` | Serie superada | ✅ arranca |
| 6.17 | HWE de 25.10 | `6.17.0-42` | Superada por el 7.0, se apaga con el phase-out | ✅ (sin validar en producción) |
| 6.18 | **Ubuntu no lo empaquetó** | — | Solo PPA mainline | — |
| **7.0** | 26.04, y HWE actual de 24.04 | `7.0.0-30.30~24.04.1` | Es a donde apunta hoy `linux-generic-hwe-24.04` | ❌ SERVER-121912 |

> **Esto ya dejó de ser un riesgo futuro.** `linux-generic-hwe-24.04` en noble-updates **ya es 7.0**.
> Un equipo sin el pin que corra `apt full-upgrade` se lleva el 7.0 y pierde MongoDB en el siguiente
> reinicio. El pin del [Caso A de la Sección 14](14-runbook-mongodb8-kernel.md#caso-a--equipo-ya-desplegado-corriendo-kernel-70) es lo único
> que lo detiene.

## C.2 ¿El 6.18 es candidato?

Tiene soporte upstream hasta **diciembre de 2028** —kernel.org lo marca `longterm`, salió el
2025-11-30—, así que a primera vista parece la salida elegante: más nuevo que el GA y más viejo que
el 6.19 que rompe MongoDB. No lo es, por tres razones:

1. **Ubuntu nunca lo empaquetó.** El salto fue 6.17 (25.10) → 7.0 (26.04). No existen los fuentes
   `linux-6.18`, `linux-hwe-6.18` ni `linux-oem-6.18` en el archivo, en ninguna serie de Ubuntu.
2. **El único camino sería el PPA mainline.** Kernels sin firmar —Secure Boot tiene que quedar
   apagado—, sin los parches de Ubuntu, sin actualizaciones de seguridad y sin metapaquete que los
   siga. Cada CVE de kernel pasa a ser trabajo manual, en cada estación.
3. **El GA tiene más cobertura, no menos.** El 6.8 de 24.04 está soportado hasta **abril de 2029**, y
   con ESM Pro hasta 2034: más que el diciembre de 2028 del 6.18 upstream, y con módulos firmados y
   headers en el archivo para que DKMS compile.

Y si la razón para querer un kernel más nuevo es hardware —la NIC del
[Caso C](14-runbook-mongodb8-kernel.md#caso-c--placas-cuya-nic-no-funciona-en-el-kernel-ga)— el kernel no es la palanca: la
respuesta es **un driver más nuevo por DKMS sobre el kernel viejo**.

## C.3 Los componentes, y cuál mira el kernel

| Componente | Versión en uso | ¿Depende del kernel? | Restricción real |
|------------|----------------|----------------------|------------------|
| **MongoDB 8.0** (`mongodb-org`, hoy 8.0.28) | repo oficial para noble | Indirecta: su TCMalloc usa `rseq` | **Techo duro: se rompe entre 6.19 y 7.0.13** (SERVER-121912). Es el único componente que fija un límite superior |
| **Driver NVIDIA `.run` 580.x** + CUDA 13.0 + cuDNN 9 | rama 580 (upstream hoy 580.178.04) | **Sí**: compila su módulo contra los headers del kernel | Techo móvil: cada kernel nuevo puede romper el build hasta que NVIDIA publique soporte. Con el kernel fijo el problema no existe |
| **`realtek-r8125-dkms`** (9.016.01; hay 9.018.00 desde 2026-07-25) | driver del fabricante | **Sí** (DKMS) | Se recompila en cada cambio de kernel. El build contra un kernel muy nuevo puede fallar; el que importa es el del GA |
| EMQX Enterprise 5 | repo de EMQX | No (BEAM, userspace) | Ninguna |
| Node.js + Node-RED | NodeSource | No | Ninguna |
| Stack ML (PyTorch y compañía, por `pip`) | sobre el python3.12 de noble | No directamente | La decide CUDA/driver, no el kernel |
| ClamAV, Lynis, Fail2Ban, UFW, `wireguard-tools`, BorgBackup, rsync | noble | No | Ninguna |
| Snaps | `snapd` de noble | No | Ninguna |

**Tres ejes, no veinte.** Un techo duro (MongoDB), un techo móvil (el `.run` de NVIDIA) y una
recompilación (DKMS). Cualquier kernel anterior a 6.19 queda debajo del techo de MongoDB, así
que un equipo que ya corre 6.11 o 6.14 no necesita bajar de versión: lo que hace falta es el pin,
para que no suba. El GA 6.8 cierra los tres problemas de una vez: queda debajo del techo de
MongoDB, es el kernel sobre el que se validó el 580.x de este manual, y vuelve deterministas las
recompilaciones de DKMS. **Mientras el kernel no se mueva, no hay matriz que mantener.**

## C.4 Auditar un equipo en un minuto

```bash
hostname
uname -r                                             # tiene que decir 6.8.0-*
apt-cache policy linux-generic-hwe-24.04 | head -3   # con el pin, el candidato es (none)
mongod --version | head -1
nvidia-smi --query-gpu=driver_version --format=csv,noheader
dkms status
dpkg-query -W -f='${Package} ${Version} ${Status}\n' \
  'linux-image-generic*' 'r8125*' 'realtek-r8125*' 2>/dev/null
```

Los scripts doctor de la [Sección 12](12-scripts-doctor.md#12-scripts-doctor-de-verificación) ya traen el chequeo de
kernel; esto agrega el inventario de versiones para archivar junto con el equipo.

---

> [Índice](../README.md#índice) · [Anterior: Anexo B: Verificación de Compatibilidad](17-anexo-b-compatibilidad.md) · [English](en/18-annex-c-kernel-matrix.md)
