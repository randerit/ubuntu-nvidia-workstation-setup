# 5. Instalación de CUDA Toolkit

> [Índice](../README.md#índice) · [Anterior: 4. Instalación de Drivers de NVIDIA en Ubuntu](04-drivers-nvidia.md) · [Siguiente: 6. Configuración Específica para Estaciones de Compresión](06-estaciones-compresion.md) · [English](en/05-cuda-toolkit.md)

> **Nota:** Esta sección instala únicamente CUDA Toolkit usando el instalador `.deb (local)` de NVIDIA. Asume que el driver NVIDIA ya está instalado vía `.run` (sección 4). **No instales el meta-paquete `cuda` ni `cuda-drivers`**: ambos arrastran el driver de NVIDIA y pisarían tu instalación `.run`. Instala solo `cuda-toolkit-XX-Y`.

> **Versión fijada por este manual:** **CUDA 13.0** (compatible con la rama de drivers 580.x.x). Si cambias de versión, ajusta los comandos y rutas (`13-0` → `XX-Y`, `cuda-13.0` → `cuda-XX.Y`).

## Antes de empezar

Confirma:

- Driver NVIDIA `.run` 580.x.x ya instalado (sección 4) y `nvidia-smi` funciona.
- Tienes internet.
- No instalaste antes CUDA por APT, snap o `.run` con otra versión.

## Paso 1: Pin del repositorio CUDA

El pin asegura prioridad correcta cuando hay paquetes solapados con otros repos:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-ubuntu2404.pin
sudo mv cuda-ubuntu2404.pin /etc/apt/preferences.d/cuda-repository-pin-600
```

> **Efecto colateral del pin:** su última regla es `Package: *` con `Pin-Priority: 600`, así que
> **todo** lo que publica NVIDIA le gana a `noble`, incluido el `dkms` que ellos reempaquetan
> (aparece como `dkms/unknown 1:3.2.1-1ubuntu2` en `apt list --upgradable`). El módulo del driver
> se construye con ese `dkms`, así que no conviene cambiarlo por uno de fuera de la distro. Un pin
> por nombre de paquete le gana al comodín y lo devuelve a Ubuntu, que sigue recibiendo sus updates
> de seguridad:
>
> ```bash
> sudo tee /etc/apt/preferences.d/99-dkms-desde-ubuntu >/dev/null <<'EOF'
> Package: dkms
> Pin: release l=NVIDIA CUDA
> Pin-Priority: -1
> EOF
> apt-cache policy dkms    # Candidate debe ser el de noble, no el 1:3.2.1
> ```
>
> Los instaladores 2.3.1+ escriben este pin solos al aplicar el de CUDA.

## Paso 2: Descarga e instala el repositorio local CUDA 13.0

```bash
wget https://developer.download.nvidia.com/compute/cuda/13.0.0/local_installers/cuda-repo-ubuntu2404-13-0-local_13.0.0-580.65.06-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2404-13-0-local_13.0.0-580.65.06-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2404-13-0-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
```

> **Importante — no cambies de versión en este paso.** El nombre del `.deb` cambia con cada release
> (`13.0.0-580.65.06-1` aquí) y con el tiempo puede dejar de estar publicado en esa ruta.
>
> Si el `wget` falla, **no** vayas a [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
> a copiar los comandos que muestra: esa página sirve **siempre la última release**, no la 13.0. Sus
> comandos instalan otro `cuda-toolkit-XX-Y`, que contradice el pin declarado arriba en esta misma
> sección y mueve el symlink `/usr/local/cuda` a la versión nueva (ver Paso 4). Ahí el equipo queda
> con dos toolkits y con `nvcc` diciendo una cosa en tu shell y otra bajo `sudo`: eso es lo que
> reprueban `workstation-doctor-analitica` / `workstation-doctor-compresion` en el check «CUDA Toolkit
> coherente».
>
> El instalador local de 13.0 está en el archivo histórico:
> [https://developer.nvidia.com/cuda-toolkit-archive](https://developer.nvidia.com/cuda-toolkit-archive)
> → CUDA Toolkit 13.0.0 → Linux > x86_64 > Ubuntu > 24.04 > deb (local).
>
> Cambiar la versión fijada es una decisión de todo el manual, no de este paso: hay que tocar también
> el Paso 4, `CUDA_VERSION_EXPECTED` en `doctor_lib.sh` y `CUDA_VERSION` en los instaladores `.deb`.
>
> **Si el equipo ya vino con otra versión instalada** (pasa: la página de descargas sirve siempre la
> última), no hace falta bajarla de versión. Desde 2.9.0 el instalador `.deb` adopta la que encuentre
> y los doctores validan **coherencia** —que `nvcc`, el symlink y `dpkg` apunten todos a la misma—,
> no el número. Lo que no se acepta es un equipo con dos toolkits y las fuentes en desacuerdo.

## Paso 3: Instala solo el toolkit (sin driver)

```bash
sudo apt-get -y install cuda-toolkit-13-0
```

> **No ejecutes** `sudo apt-get install cuda` ni `sudo apt-get install cuda-drivers`. Esos paquetes instalan el driver de NVIDIA empaquetado y rompen el driver `.run` 580.x.x instalado en la sección 4.

**Verificación (opcional):**
```bash
dpkg -l | grep cuda-toolkit-13-0
ls /usr/local/cuda-13.0/bin/nvcc
```

## Paso 4: Fija el symlink de CUDA y configura PATH y LD_LIBRARY_PATH

Los paquetes de NVIDIA registran `/usr/local/cuda` en `update-alternatives` con prioridad por
versión: si el equipo tuvo alguna vez otro toolkit, el más nuevo gana solo y nada lo devuelve. Fijalo
en la versión del manual:

```bash
sudo update-alternatives --set cuda /usr/local/cuda-13.0
```

> **Por qué importa:** los scripts `workstation-doctor-*` corren con `sudo`, y bajo `sudo` no se lee tu
> `~/.bashrc`. El `nvcc` que ve el doctor es el de este symlink, no el de tu PATH interactivo. Un
> equipo con el `.bashrc` correcto y el symlink apuntando a otra versión da `[FALLO]` igual.

Ahora edita `~/.bashrc`:

```bash
nano ~/.bashrc
```

Agrega al final:

```bash
export PATH=/usr/local/cuda-13.0/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-13.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

Guarda y recarga:

```bash
source ~/.bashrc
```

**Verificación:**
```bash
readlink -f /usr/local/cuda   # /usr/local/cuda-13.0
which nvcc                # /usr/local/cuda-13.0/bin/nvcc
nvcc --version            # release 13.0
/usr/local/cuda/bin/nvcc --version   # lo que ve el doctor (sin tu PATH): release 13.0
nvidia-smi                # driver 580.x.x sigue cargado
```

## Si necesitas desinstalar CUDA Toolkit

```bash
sudo apt-get -y remove --purge 'cuda-toolkit-13-0' 'cuda-*-13-0'
sudo apt-get -y autoremove
sudo rm -rf /usr/local/cuda-13.0
sudo rm -f /etc/apt/preferences.d/cuda-repository-pin-600
sudo rm -f /etc/apt/sources.list.d/cuda-ubuntu2404-13-0-local.list
sudo apt-get update
```

El driver NVIDIA `.run` no se toca con esto.

## Troubleshooting CUDA

- **`nvcc: command not found`:** revisa que `~/.bashrc` tenga la línea `export PATH=...` y que ejecutaste `source ~/.bashrc`.
- **El doctor da `[FALLO] CUDA Toolkit coherente` pero tu `nvcc --version` dice 13.0:** el doctor corre con `sudo` y lee `/usr/local/cuda`, no tu `~/.bashrc`. Compará con `readlink -f /usr/local/cuda` y aplicá el `update-alternatives --set` del Paso 4. El doctor imprime las tres fuentes (nvcc, symlink y dpkg) en el mensaje, así que se ve cuál es la que discrepa.
- **El equipo tiene CUDA 13.1 o 13.4 en vez de 13.0:** no es un error en sí. El doctor lo informa con `[INFO]` y solo reprueba si las fuentes no coinciden; el instalador `.deb` 2.9.0+ adopta esa versión en vez de bajar otros ~5 GB. Si igual querés la del manual: `sudo nvidia-cuda-setup --cuda-version 13.0`.
- **Tenés dos toolkits instalados (`ls -d /usr/local/cuda-*` muestra más de uno):** alguien siguió los comandos de la página de descargas de NVIDIA en vez del Paso 2. No hace falta purgar: alcanza con fijar el symlink del Paso 4. Si querés recuperar el espacio (~5 GB por toolkit), revisá primero `sudo apt-get -s purge 'cuda-toolkit-XX-Y' 'cuda-*-XX-Y'` antes de ejecutarlo sin `-s`.
- **`apt` quiere instalar `nvidia-driver-*` o `cuda-drivers-*`:** estás llamando al meta-paquete `cuda`. Usa solo `cuda-toolkit-13-0`.
- **El driver dejó de funcionar después de instalar CUDA:** instalaste `cuda` o `cuda-drivers`. Purga con la sección de desinstalación, reinstala el driver `.run` (sección 4) y vuelve a instalar solo `cuda-toolkit-13-0`.
- **`nvidia-smi` y `nvcc` reportan versiones distintas:** es normal. `nvidia-smi` muestra la versión del driver, `nvcc` la del toolkit.

---

> [Índice](../README.md#índice) · [Anterior: 4. Instalación de Drivers de NVIDIA en Ubuntu](04-drivers-nvidia.md) · [Siguiente: 6. Configuración Específica para Estaciones de Compresión](06-estaciones-compresion.md) · [English](en/05-cuda-toolkit.md)
