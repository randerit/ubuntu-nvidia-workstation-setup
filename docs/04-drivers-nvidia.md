# 4. Instalación de Drivers de NVIDIA en Ubuntu

> [Índice](../README.md#índice) · [Anterior: 3. Preparación Inicial del Sistema Ubuntu](03-preparacion-del-sistema.md) · [Siguiente: 5. Instalación de CUDA Toolkit](05-cuda-toolkit.md) · [English](en/04-nvidia-drivers.md)

Esta sección instala el driver NVIDIA oficial usando el archivo `.run`. Este es el método principal del manual.

## Antes de empezar

Confirma que ya hiciste la sección 3:

- Ubuntu está actualizado.
- Hay internet.
- `gcc`, `dkms` y los headers del kernel están instalados.
- Secure Boot está desactivado en BIOS/UEFI.
- No instalaste NVIDIA desde "Additional Drivers", `ubuntu-drivers` ni APT.

> **Importante:** No mezcles métodos. Si instalas NVIDIA con `.run`, no instales después `nvidia-driver-XXX`, `nvidia-open` ni `cuda-drivers` con APT sobre la misma instalación.

## Rama recomendada: 580.x.x

Para estas estaciones usamos la familia **R580 / 580.x.x** porque ha sido la más estable en nuestras pruebas. Cuando descargues el driver, busca la versión más reciente disponible dentro de la rama 580 para tu GPU.

No cambies a otra familia de drivers solo porque exista una versión más nueva. Cambia de rama únicamente si hay una razón concreta: soporte de una GPU nueva, bug crítico corregido o validación interna.

## Paso 1: Identifica la GPU NVIDIA

Ejecuta:

```bash
lspci -nn | grep -Ei 'nvidia|vga|3d|display'
```

Ejemplo:

```
01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3070] (rev a1)
```

Si no aparece una GPU NVIDIA:

- Revisa que la GPU esté bien instalada físicamente.
- Revisa BIOS/UEFI.
- No sigas con el `.run` hasta que el sistema detecte la GPU.

## Paso 2: Descarga el driver `.run`

1. Entra a [https://www.nvidia.com/drivers/](https://www.nvidia.com/drivers/).
2. Selecciona tu modelo exacto de GPU.
3. Selecciona **Linux 64-bit** como sistema operativo.
4. Busca una versión **580.x.x**.
5. Descarga el archivo `.run`.
6. Guárdalo en `Downloads`.

Si NVIDIA ofrece varias opciones, prefiere la más reciente de la familia 580 compatible con tu GPU. Si la web no ofrece 580 para ese modelo, detente y revisa compatibilidad antes de instalar otra familia.

En la terminal, confirma que el archivo existe:

```bash
cd ~/Downloads
ls NVIDIA-Linux-x86_64-*.run
mv NVIDIA-Linux-x86_64-*.run NVIDIA-driver.run
```

Si `mv` falla porque hay más de un `.run`, deja en `Downloads` solo el driver que vas a instalar y repite el comando.

Si NVIDIA publica checksum para tu descarga, compáralo:

```bash
sha256sum NVIDIA-driver.run
```

## Paso 3: Limpia instalaciones NVIDIA previas

En un equipo recién instalado no debería haber mucho que limpiar, pero este paso evita mezclar métodos:

```bash
dpkg -l | grep -Ei 'nvidia|cuda-drivers' || true
sudo apt purge -y '^nvidia-.*' '^libnvidia-.*' '^cuda-drivers.*' '^nvidia-open.*'
sudo apt autoremove -y
```

Si el comando elimina algo, reinicia antes de seguir:

```bash
sudo reboot
```

## Paso 4: Desactiva Nouveau y entra a modo texto

`nouveau` es el driver libre que Ubuntu puede cargar antes de instalar NVIDIA. El `.run` necesita que no esté activo.

```bash
printf 'blacklist nouveau\noptions nouveau modeset=0\n' | sudo tee /etc/modprobe.d/blacklist-nouveau.conf
sudo update-initramfs -u
sudo systemctl set-default multi-user.target
sudo reboot
```

Después del reinicio verás una consola de texto. Inicia sesión con tu usuario y verifica:

```bash
lsmod | grep nouveau
```

Resultado esperado: no muestra nada. Si aparece `nouveau`, no sigas; repite este paso y reinicia.

## Paso 5: Ejecuta el instalador `.run`

Desde la consola de texto:

```bash
cd ~/Downloads
chmod +x NVIDIA-driver.run
sudo ./NVIDIA-driver.run --dkms
```

Responde así si el instalador pregunta:

| Pregunta del instalador | Respuesta recomendada |
|-------------------------|-----------------------|
| `The distribution-provided pre-install script failed...` | `Yes`, continuar. En Ubuntu suele ser una advertencia. |
| Registrar módulos con DKMS | `Yes`. Esto ayuda cuando cambia el kernel. |
| Tipo de módulo: Open/MIT-GPL o Proprietary | Para RTX 20/30/40/50 o más nuevas, usa Open/MIT-GPL si aparece. Para GPUs antiguas pre-Turing, usa Proprietary. Si no sabes, deja la opción recomendada por el instalador. |
| Bibliotecas 32-bit | `No`, salvo que necesites aplicaciones antiguas de 32 bits. |
| Ejecutar `nvidia-xconfig` | `No`. |

Si falla, revisa:

```bash
less /var/log/nvidia-installer.log
```

## Paso 6: Vuelve al modo gráfico y reinicia

Cuando el instalador termine correctamente:

```bash
sudo systemctl set-default graphical.target
sudo reboot
```

## Paso 7: Verifica el driver NVIDIA

Después del reinicio, abre una terminal y ejecuta:

```bash
nvidia-smi
cat /proc/driver/nvidia/version
dkms status | grep -i nvidia
```

Resultado esperado:

- `nvidia-smi` muestra la GPU.
- `/proc/driver/nvidia/version` muestra la versión cargada.
- `dkms status` muestra el módulo NVIDIA instalado para el kernel actual.

También puedes guardar un resumen del equipo:

```bash
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
```

## Si necesitas desinstalar el `.run`

Usa esto solo si el driver quedó mal instalado o necesitas empezar de cero:

```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

Luego inicia sesión en consola y ejecuta:

```bash
sudo nvidia-uninstall
sudo rm -f /etc/modprobe.d/blacklist-nouveau.conf
sudo update-initramfs -u
sudo systemctl set-default graphical.target
sudo reboot
```

## Si algo falla con NVIDIA

| Problema | Qué revisar primero |
|----------|---------------------|
| `nvidia-smi` dice que falló | Revisa Secure Boot, reinicia y mira `/var/log/nvidia-installer.log`. |
| El instalador dice que `nouveau` está activo | Repite el paso 4, ejecuta `sudo update-initramfs -u` y reinicia. |
| Falla compilando el módulo | Verifica `gcc --version`, `dkms status` y `ls /usr/src/linux-headers-$(uname -r)`. |
| Pantalla negra después del reinicio | Entra por modo recovery o TTY, ejecuta `sudo nvidia-uninstall` y vuelve a intentar. |
| Se rompió después de actualizar kernel | Instala headers del kernel nuevo y ejecuta `sudo dkms autoinstall`. |
| Instalaste por APT por error | Purga paquetes NVIDIA con APT, reinicia y repite esta sección desde el paso 3. |

Referencias oficiales:

- [NVIDIA Driver Installation Guide](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/)
- [NVIDIA Driver Downloads](https://www.nvidia.com/drivers/)

---

> [Índice](../README.md#índice) · [Anterior: 3. Preparación Inicial del Sistema Ubuntu](03-preparacion-del-sistema.md) · [Siguiente: 5. Instalación de CUDA Toolkit](05-cuda-toolkit.md) · [English](en/04-nvidia-drivers.md)
