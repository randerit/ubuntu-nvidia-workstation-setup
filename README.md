# Ubuntu NVIDIA Workstation Setup

Guía y scripts para dejar operativa una estación de trabajo Ubuntu o Linux Mint con GPU NVIDIA: instalación, drivers por `.run`, CUDA, servicios de las estaciones, diagnóstico y recuperación de red, Wake-on-LAN y endurecimiento básico. Cada capítulo explica el porqué de cada paso y cómo verificar que quedó bien.

[English](README_en.md)

## Qué cubre

- **Sistemas:** Ubuntu 24.04 LTS como referencia, con notas para 22.04. Linux Mint 21.x (base 22.04) y 22.x (base 24.04). LMDE no está soportado.
- **GPU:** NVIDIA GeForce RTX series 20, 30, 40 y 50, con el driver `.run` de la rama 580.x y CUDA 13.0.
- **Perfiles de estación:** compresión, analítica y visualización.

## Índice

| Capítulo | Contenido |
|----------|-----------|
| [Introducción](docs/00-introduccion.md) | Resumen del proceso completo |
| [1. Requisitos previos](docs/01-requisitos-previos.md) | Qué preparar y compatibilidad con Mint |
| [2. Instalación de Ubuntu](docs/02-instalacion-ubuntu.md) | USB, BIOS/UEFI e instalación |
| [3. Preparación del sistema](docs/03-preparacion-del-sistema.md) | Actualizaciones, Xorg, acceso remoto y ajustes por versión |
| [4. Drivers NVIDIA](docs/04-drivers-nvidia.md) | Instalación con `.run`, verificación y desinstalación |
| [5. CUDA Toolkit](docs/05-cuda-toolkit.md) | Repositorio local, toolkit y variables de entorno |
| [6. Estaciones de compresión](docs/06-estaciones-compresion.md) | MongoDB, EMQX, GStreamer y soporte remoto |
| [7. Estaciones de analítica](docs/07-estaciones-analitica.md) | MongoDB con usuario, Node-RED y Python para ML |
| [8. Interfaz gráfica](docs/08-interfaz-grafica.md) | Activar y desactivar el entorno gráfico |
| [9. Redes en placas nuevas](docs/09-redes-placas-nuevas.md) | Realtek RTL8125, Intel, Wi-Fi, DNS e IP estática |
| [10. Wake-on-LAN](docs/10-wake-on-lan.md) | Configuración y envío del paquete mágico |
| [11. Script de post-instalación](docs/11-script-post-instalacion.md) | Preparación inicial automatizada |
| [12. Scripts doctor](docs/12-scripts-doctor.md) | Verificación e instalación de faltantes |
| [13. Seguridad](docs/13-seguridad.md) | SSH, firewall, fail2ban y actualizaciones |
| [14. Runbook MongoDB 8 y kernel](docs/14-runbook-mongodb8-kernel.md) | Qué hacer si `mongod` no arranca con el kernel HWE 7.0 |
| [FAQ](docs/15-faq.md) | Preguntas frecuentes |
| [Anexo A](docs/16-anexo-a-gpus-nvidia.md) · [B](docs/17-anexo-b-compatibilidad.md) · [C](docs/18-anexo-c-matriz-kernel.md) | Identificación de GPU, compatibilidad y matriz de kernels |
| [Pruebas manuales](docs/pruebas-manuales.md) | Cómo verificar el repositorio y un equipo real |

## Inicio rápido

1. Lee los [requisitos previos](docs/01-requisitos-previos.md) y sigue los capítulos 2 a 5 en orden.
2. Según el tipo de equipo, continúa con el capítulo [6](docs/06-estaciones-compresion.md) o el [7](docs/07-estaciones-analitica.md).
3. Verifica el resultado con el doctor del perfil correspondiente:

```bash
git clone https://github.com/randerit/ubuntu-nvidia-workstation-setup.git
cd ubuntu-nvidia-workstation-setup
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh      # o doctor_analitica.sh / doctor_visualizacion.sh
```

Sin `--fix` los doctor solo leen. Con `--fix` instalan lo que falte; úsalo primero en un equipo de pruebas.

## Scripts

Todos viven en [`scripts/`](scripts/) y se ejecutan desde la raíz del repositorio. Las librerías se buscan junto a cada script, así que al copiarlos a otro equipo conviene llevarse la carpeta completa.

| Script | Para qué sirve | Modifica el sistema |
|--------|----------------|---------------------|
| [`doctor_compresion.sh`](scripts/doctor_compresion.sh) | Verifica (y con `--fix` instala) lo de una estación de compresión | Solo con `--fix` |
| [`doctor_analitica.sh`](scripts/doctor_analitica.sh) | Lo mismo para una estación de analítica | Solo con `--fix` |
| [`doctor_visualizacion.sh`](scripts/doctor_visualizacion.sh) | Lo mismo para una estación de visualización | Solo con `--fix` |
| [`diag-nic.sh`](scripts/diag-nic.sh) | Diagnóstico por capas de un puerto de red | No |
| [`fix-r8125-downgrade-6.8.sh`](scripts/fix-r8125-downgrade-6.8.sh) | Prepara el driver Realtek y el kernel GA 6.8 antes de reiniciar (`--dry-run` para simular) | Sí |
| [`doctor_lib.sh`](scripts/doctor_lib.sh), [`nic_lib.sh`](scripts/nic_lib.sh) | Librerías compartidas; no se ejecutan directamente | No |
| [`verificar_repo.sh`](scripts/verificar_repo.sh) | `shellcheck`, self-checks y enlaces de la documentación | No |
| [`self_check_doctor_lib.sh`](scripts/self_check_doctor_lib.sh), [`self_check_nic_lib.sh`](scripts/self_check_nic_lib.sh) | Pruebas de las librerías contra árboles falsos | No |
| [`check_links.py`](scripts/check_links.py) | Comprueba los enlaces relativos de los `.md` | No |

Detalles de uso y códigos de salida en el [capítulo 12](docs/12-scripts-doctor.md).

## Estructura

```text
.
├── README.md, README_en.md
├── docs/            Capítulos en español; docs/en/ tiene la versión en inglés
├── scripts/         Doctores, diagnóstico de red, librerías y verificaciones
└── LICENSE
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
