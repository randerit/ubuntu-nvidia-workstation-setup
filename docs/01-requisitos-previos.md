# 1. Requisitos Previos a la Instalación

> [Índice](../README.md#índice) · [Anterior: Introducción](00-introduccion.md) · [Siguiente: 2. Instalación del Sistema Ubuntu](02-instalacion-ubuntu.md) · [English](en/01-requirements.md)

## Antes de tocar el equipo

Confirma estos puntos antes de instalar Ubuntu:

| Necesitas | Para qué sirve |
|-----------|----------------|
| USB de 8 GB o más | Para arrancar el instalador de Ubuntu. |
| Imagen ISO de Ubuntu Desktop LTS | Es el archivo que se copia a la USB. Esta guía usa Ubuntu Desktop 24.04 LTS como referencia. |
| Respaldo de datos importantes | La instalación puede borrar el disco completo. |
| Acceso a internet | Ayuda a instalar actualizaciones y paquetes durante el proceso. |
| Tipo de estación definido | Decide si el equipo será de **compresión/data** o de **analítica**. |

> **Alerta importante:** Si el equipo tiene archivos que no puedes perder, respáldalos antes de seguir. El modo simple de instalación usa "Borrar disco e instalar Ubuntu".

## Decisión rápida

- Si el equipo será usado por una persona y tendrá pantalla, instala **Ubuntu Desktop**.
- Si el equipo será administrado remotamente, igual puedes partir con **Ubuntu Desktop** y luego desactivar la interfaz gráfica.
- Si necesitas dual boot con Windows, no uses el camino simple de esta sección; requiere particionado manual.

## Ubuntu y derivados directos (Linux Mint)

El manual está escrito para Ubuntu LTS, y también sirve para los derivados directos que
reempaquetan Ubuntu sin cambiar la base: **Linux Mint 21.x (base 22.04)** y **Linux Mint 22.x
(base 24.04)**. Lo que importa es la base, no el número de la distro: Mint 22.1 no es Ubuntu
22.04, es Ubuntu 24.04 reempaquetado. Comprueba la base con:

```bash
cat /etc/upstream-release/lsb-release
```

Debe decir `DISTRIB_ID=Ubuntu` y `DISTRIB_RELEASE=24.04` (o `22.04`). Si el archivo no existe,
mira `UBUNTU_CODENAME` en `/etc/os-release` (`noble` = 24.04, `jammy` = 22.04).

> **No uses `lsb_release -cs` en un derivado.** En Mint devuelve su propio codename
> (`wilma`, `xia`, `virginia`), que no existe en los repositorios de Ubuntu, NVIDIA, MongoDB
> ni EMQX: cualquier repo armado con ese valor da 404. Usa siempre `noble` o `jammy` según la
> base.

Tres diferencias de Mint que sí cambian pasos de este manual:

| Diferencia | Qué implica |
|-----------|-------------|
| `/etc/apt/preferences.d/nosnap.pref` bloquea `snapd` | Con ese pin (`-10`) `apt` deja `snapd` sin candidato y los pasos por snap (Go, VS Code) no corren. Para habilitarlos: `sudo cp -a /etc/apt/preferences.d/nosnap.pref /var/backups/nosnap.pref.bak && sudo rm /etc/apt/preferences.d/nosnap.pref && sudo apt-get update`. Revertir es un `mv` del respaldo. Los instaladores 2.5.0+ y `workstation-doctor-compresion --fix` lo hacen solos, salvo con `--skip-snaps`. |
| El gestor de sesión es LightDM, no GDM | Los ajustes de `/etc/gdm3/custom.conf` (por ejemplo desactivar Wayland) no aplican: Mint ya corre X11 con Cinnamon. Para apagar la interfaz gráfica usa `lightdm` en lugar de `gdm3`. |
| El Gestor de Actualizaciones de Mint ofrece kernels | Si fijaste el kernel por MongoDB 8, no instales kernels desde ahí; el pin de `apt` no cubre lo que se instale a mano. El 6.14 que trae Mint 22.2 es compatible y **no** hay que bajarlo a 6.8. |

LMDE (Linux Mint Debian Edition) **no** sirve: su base es Debian, no Ubuntu, y los
instaladores la rechazan.

---

> [Índice](../README.md#índice) · [Anterior: Introducción](00-introduccion.md) · [Siguiente: 2. Instalación del Sistema Ubuntu](02-instalacion-ubuntu.md) · [English](en/01-requirements.md)
