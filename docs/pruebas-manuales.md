# Pruebas manuales

> [Índice](../README.md#índice) · [Scripts doctor](12-scripts-doctor.md) · [English](en/manual-tests.md)

Esta guía describe cómo comprobar, en el repositorio y en un equipo real, que lo documentado y los scripts funcionan. Las pruebas están ordenadas de menos a más invasivas: las dos primeras no tocan el sistema.

## 1. Verificación del repositorio (sin tocar el sistema)

Desde la raíz del repositorio:

```bash
./scripts/verificar_repo.sh
```

Ejecuta, en este orden:

| Paso | Qué comprueba | Resultado esperado |
|------|---------------|--------------------|
| `shellcheck scripts/*.sh` | Errores comunes de shell en todos los scripts. Si no está instalado, el paso se omite (`sudo apt install shellcheck`). | Sin hallazgos |
| `self_check_doctor_lib.sh` | Chequeos de `doctor_lib.sh` contra árboles falsos en un directorio temporal. | `OK: todos los self-checks pasaron` |
| `self_check_nic_lib.sh` | `nic_lib.sh` y las reglas de `diag-nic.sh` contra los escenarios A–I de terreno. | `OK: todos los self-checks pasaron` |
| `scripts/check_links.py` | Que los enlaces relativos y las anclas de todos los `.md` apunten a algo que existe. | `0 rotos` |

Hazlo antes de copiar los scripts a un equipo y cada vez que cambies una librería. Los self-checks no necesitan root, hardware ni red.

Los hallazgos de `shellcheck` que se suprimieron a propósito llevan un comentario `# shellcheck disable=...` con el motivo, justo encima de la línea.

## 2. Simulación de cambios (`--dry-run`)

Para ver qué haría la remediación de red sin modificar nada:

```bash
sudo ./scripts/fix-r8125-downgrade-6.8.sh --dry-run
```

Resultado esperado: el script informa cada fase (conectividad, detección del chip, kernel GA 6.8) y termina sin cambiar la configuración, sin instalar paquetes y sin programar un reinicio: solo escribe su log en `/var/log/nic-kernel-downgrade.log` y marca cada acción como `(dry-run)`.

## 3. Equipo de pruebas: guía paso a paso

Usa un equipo (o una máquina virtual con GPU en passthrough) que se pueda formatear. Cada fila corresponde a un capítulo de la guía; ejecuta su verificación y compara con el resultado esperado.

| Capítulo | Comando | Resultado esperado |
|----------|---------|--------------------|
| [3. Preparación](03-preparacion-del-sistema.md) | `gcc --version`, `dkms status`, `ls /usr/src/linux-headers-$(uname -r)`, `echo $XDG_SESSION_TYPE` | Compilador presente, headers del kernel en uso, sesión `x11` |
| [4. Drivers NVIDIA](04-drivers-nvidia.md) | `nvidia-smi` y `dkms status \| grep -i nvidia` | La GPU aparece y el módulo está construido para el kernel actual |
| [5. CUDA](05-cuda-toolkit.md) | `nvcc --version`, `readlink -f /usr/local/cuda`, `which nvcc` | La misma versión (13.0) en las tres respuestas |
| [6. Compresión](06-estaciones-compresion.md) / [7. Analítica](07-estaciones-analitica.md) | `systemctl status mongod emqx` (según el perfil) | Servicios en `active (running)` |
| [14. Runbook MongoDB](14-runbook-mongodb8-kernel.md) | `uname -r` y `apt-cache policy linux-generic-hwe-24.04` | Kernel anterior a 6.19 y `Candidate: (none)` si el equipo está fijado en GA |

## 4. Scripts doctor en un equipo

Primero solo verificar, sin instalar nada:

```bash
chmod +x scripts/*.sh
./scripts/doctor_compresion.sh     # o doctor_analitica.sh / doctor_visualizacion.sh
```

Resultado esperado: una línea por componente y un resumen con los cuatro niveles de alerta descritos en el [capítulo 12](12-scripts-doctor.md). Un equipo bien instalado termina sin fallas necesarias.

Para provocar un hallazgo controlado y comprobar que el doctor lo detecta, desactiva un servicio no crítico (por ejemplo `sudo systemctl stop emqx`), vuelve a correr el doctor y confirma que lo marca; después `sudo systemctl start emqx`. Para probar `--fix`, ejecútalo solo en el equipo de pruebas:

```bash
./scripts/doctor_compresion.sh --fix
```

Resultado esperado: instala lo que falte, vuelve a verificar y deja el log completo en `/tmp/doctor_fix_AAAAMMDD_HHMMSS.log`.

## 5. Diagnóstico de red

En un equipo con una NIC Realtek 2.5GbE (o cualquier interfaz, para ver el formato del informe):

```bash
sudo ./scripts/diag-nic.sh <interfaz> 20
```

Resultado esperado: el script solo lee y captura. Termina con uno de estos códigos de salida:

| Código | Significado |
|--------|-------------|
| 0 | Sin hallazgos por encima de informativo |
| 1 | Avisos de configuración o persistencia |
| 2 | Sospechas que requieren más evidencia |
| 3 | Fallo confirmado de driver, hardware o enlace |

## 6. Qué registrar

Al terminar, anota por equipo: versión de Ubuntu o Linux Mint, kernel (`uname -r`), GPU y driver (`nvidia-smi --query-gpu=name,driver_version --format=csv`), perfil del doctor que corriste y su resumen. No pegues en issues ni en commits direcciones IP, MAC, nombres de equipos ni contraseñas: usa valores de ejemplo (rango `192.0.2.0/24` para IP, `00:00:5E:00:53:xx` para MAC).
