# Anexo B: Verificación de Compatibilidad

> [Índice](../README.md#índice) · [Anterior: Anexo A: Identificación de GPUs NVIDIA](16-anexo-a-gpus-nvidia.md) · [Siguiente: Anexo C: Matriz de Compatibilidad de Kernel (Ubuntu 24.04 LTS)](18-anexo-c-matriz-kernel.md) · [English](en/17-annex-b-compatibility.md)

> **Nota:** Antes de instalar drivers o CUDA, verifica compatibilidad para evitar errores. Usa comandos para checkear versiones instaladas. Si hay incompatibilidades, actualiza o downgradéa según necesidad.

## Verificar Versiones Instaladas
Ejecuta estos comandos para confirmar tu setup actual:

### Driver NVIDIA
```bash
nvidia-smi  # Muestra versión driver, CUDA runtime, GPU
# Ejemplo salida: Driver Version: 580.159.03
```

### CUDA Toolkit
```bash
nvcc --version  # Versión del compilador CUDA
# Si no está instalado: "Command 'nvcc' not found"
```

### Ubuntu Kernel y GCC
```bash
uname -r  # Versión kernel (ej. 6.8.0-40-generic)
gcc --version | head -1  # Versión GCC (ej. gcc 11.4.0)
```

## Compatibilidad Recomendada (Mayo 2026)
Basado en NVIDIA docs y validación interna. Para este manual, la combinación estándar es **driver 580.x.x (`.run`) + CUDA Toolkit 13.0 (`.deb local`)**.

### Drivers NVIDIA y GPUs
| Serie GPU | Arquitectura | Mínimo técnico aproximado | Rama recomendada del manual |
|-----------|--------------|---------------------------|----------------------------|
| RTX 3000 (Ampere) | GA10x | 470.x | 580.x.x |
| RTX 4000 (Ada Lovelace) | AD10x | 525.x | 580.x.x |
| RTX 5000 (Blackwell) | GB20x | 570.x/580.x según modelo | 580.x.x |

**Nota:** Instala la versión más reciente disponible dentro de la familia 580 para tu GPU. No cambies de rama sin validar primero.

### CUDA Toolkit y Drivers
| CUDA Toolkit | Driver mínimo recomendado | Soporte Ubuntu | Estado en este manual |
|--------------|---------------------------|----------------|-----------------------|
| 13.0 | 580.65.06 | 22.04, 24.04 | **Versión fijada** |
| 12.8 | 570.x | 22.04, 24.04 | Compatible, no recomendada en este manual |
| 12.6 | 560.x | 20.04, 22.04, 24.04 | Legacy |

**Nota:** El manual fija CUDA 13.0 con driver `.run` 580.x.x. Usa otras versiones solo si tu hardware o software lo exige.

## Cómo Verificar Compatibilidad Online
1. **Para Drivers:** Ve a [NVIDIA Drivers](https://www.nvidia.com/drivers/), selecciona tu GPU y OS.
2. **Para CUDA:** Ve a [CUDA Downloads](https://developer.nvidia.com/cuda-downloads), elige tu OS y GPU. Selecciona siempre el instalador `deb (local)`.

## Troubleshooting de Compatibilidades
- **Driver demasiado viejo para CUDA:** Instala un driver NVIDIA más reciente siguiendo la sección 4 con archivo `.run`.
- **CUDA no reconoce GPU:** Verifica con `nvidia-smi`. Si falla, reinstala drivers.
- **`apt` quiere instalar `nvidia-driver-*` al instalar CUDA:** estás llamando a un meta-paquete (`cuda` o `cuda-drivers`). Usa solo `cuda-toolkit-XX-Y`.
- **Kernel mismatch:** **no** actualices el kernel para arreglarlo. En 24.04 el kernel está fijado en el track GA 6.8 por MongoDB ([Sección 14](14-runbook-mongodb8-kernel.md)), y hoy `apt upgrade` sin el pin trae el 7.0 por HWE. Instalá los headers del kernel que ya estás corriendo (`sudo apt install linux-headers-$(uname -r)`) y reinstalá el `.run`. Ver [Anexo C](18-anexo-c-matriz-kernel.md#anexo-c-matriz-de-compatibilidad-de-kernel-ubuntu-2404-lts).
- **GCC incompatible:** Instala versión correcta: `sudo apt install gcc-12 g++-12` y reconfigura con `update-alternatives` si es necesario.

## Tips Generales
- **Instala en orden:** Driver `.run` (sección 4) → CUDA Toolkit `.deb local` (sección 5).
- **Prueba con samples:** clona [https://github.com/NVIDIA/cuda-samples](https://github.com/NVIDIA/cuda-samples) y compila `deviceQuery` para validar GPU + toolkit.
- **Si usas Docker:** instala `nvidia-container-toolkit` (no `nvidia-docker2`, deprecado) y ejecuta con `docker run --gpus all`.
- **Backup antes de cambios:** Crea snapshot o backup de drivers.

> **Recursos Adicionales:**
> * [NVIDIA CUDA Toolkit Release Notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)
> * [NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
> * [Ubuntu NVIDIA Drivers PPA](https://launchpad.net/~graphics-drivers/+archive/ubuntu/ppa)

---

> [Índice](../README.md#índice) · [Anterior: Anexo A: Identificación de GPUs NVIDIA](16-anexo-a-gpus-nvidia.md) · [Siguiente: Anexo C: Matriz de Compatibilidad de Kernel (Ubuntu 24.04 LTS)](18-anexo-c-matriz-kernel.md) · [English](en/17-annex-b-compatibility.md)
