# 7. Configuración Específica para Estaciones de Analítica

> [Índice](../README.md#índice) · [Anterior: 6. Configuración Específica para Estaciones de Compresión](06-estaciones-compresion.md) · [Siguiente: 8. Gestión de la Interfaz Gráfica](08-interfaz-grafica.md) · [English](en/07-analytics-workstations.md)

> **Nota:** Esta sección instala herramientas para analítica/machine learning, asumiendo Ubuntu 24.04.1 LTS con CUDA instalado. Instala solo lo necesario.

## Configuración de MongoDB (Base de Datos y Usuario)

### Paso 1: Accede a la Consola
```bash
mongosh
```

### Paso 2: Crea Base de Datos y Usuario
Reemplaza placeholders:
```javascript
use NOMBRE_BD
db.createUser({
  user: "USUARIO",
  pwd: "PASSWORD",
  roles: [
    {
      role: "readWrite",
      db: "NOMBRE_BD"
    }
  ]
})
```

Sal con `exit`.

### Paso 3: Habilita Autorización
Edita config:
```bash
sudo nano /etc/mongod.conf
```

Agrega bajo `security:`:
```yaml
security:
  authorization: enabled
```

Guarda y reinicia:
```bash
sudo systemctl restart mongod
```

**Verificación (opcional):**
```bash
mongosh -u USUARIO -p PASSWORD --authenticationDatabase NOMBRE_BD
# Debería conectar
```

## Instalación de Node-RED

### Paso 1: Ejecuta el Script de Instalación
> **Advertencia de seguridad:** Revisa el contenido del script antes de ejecutarlo. Puedes descargarlo primero con `wget` e inspeccionarlo.

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```

### Paso 2: Habilita y Inicia el Servicio
```bash
sudo systemctl enable nodered
sudo systemctl start nodered
```

**Verificación (opcional):**
```bash
sudo systemctl status nodered
# Dashboard en http://localhost:1880
```

## Instalación de Python y Bibliotecas para Machine Learning

### Paso 1: Instala Python y Pip
```bash
sudo apt install -y python3 python3-pip
```

### Paso 2: Actualiza Pip
```bash
pip3 install --upgrade pip --break-system-packages
```

> Si este paso corta con `Cannot uninstall pip ... RECORD file not found`, es el mismo caso que
> explica el Paso 3: aplicá la receta de ahí usando `pip` como paquete en conflicto.

### Paso 3: Instala Bibliotecas
> **Nota:** Se usa `--break-system-packages` para instalar a nivel de sistema, permitiendo acceso directo desde cualquier script Python sin necesidad de entornos virtuales.

```bash
pip3 install --break-system-packages pandas numpy scikit-learn paho-mqtt ultralytics
```

> **Si corta con `ERROR: Cannot uninstall typing_extensions 4.10.0, RECORD file not found`:** es lo
> esperable en Ubuntu 24.04, no un error tuyo. `ultralytics` arrastra `torch`, que pide un
> `typing_extensions` más nuevo que el de la distro. Ese paquete lo puso `apt` en
> `/usr/lib/python3/dist-packages` **sin archivo `RECORD`** —dpkg no lo escribe—, así que pip no
> sabe qué archivos borrar para reemplazarlo y **aborta la instalación entera**: no queda instalada
> ni una de las cinco bibliotecas, aunque el log liste decenas de descargas.
>
> Instalá una copia propia del paquete en conflicto y repetí:
>
> ```bash
> pip3 install --break-system-packages --ignore-installed typing_extensions
> pip3 install --break-system-packages pandas numpy scikit-learn paho-mqtt ultralytics
> ```
>
> `--ignore-installed` **no** borra el archivo de `apt`: dpkg queda intacto y los paquetes del
> sistema que dependen de él siguen funcionando. Instala la copia nueva en
> `/usr/local/lib/python3.12/dist-packages`, que va antes en `sys.path` y gana al importar. Por eso
> `sudo apt remove python3-typing-extensions` **no** es la salida: se lleva puestos paquetes del
> sistema.
>
> Si el nombre del paquete en conflicto es otro, cambialo en la primera línea. Desde 2.8.9,
> el instalador del perfil analítica (`workstation-analytics` en 2.x, hoy
> `workstation-dependencies --perfil analitica`) hace este reintento solo.

**Verificación (opcional):**
```bash
python3 -c "import pandas, numpy, sklearn; print('Bibliotecas OK')"
# Debería imprimir sin errores
```

## Configuración de Puertos para Estaciones de Analítica (Opcional)
Si usas firewall, abre puertos:

| Aplicación | Puertos | Protocolo | Comando |
|------------|---------|-----------|---------|
| MongoDB | 27017 | TCP | `sudo ufw allow 27017/tcp` |
| Node-RED | 1880 | TCP | `sudo ufw allow 1880/tcp` |

**Verificación (opcional):**
```bash
sudo ufw status
```

## Tips Generales
- Para proyectos propios, usa entornos virtuales: `python3 -m venv ml_env && source ml_env/bin/activate`. Las bibliotecas del Paso 3 van a nivel de sistema a propósito, para que cualquier script las vea sin activar nada.
- Actualiza bibliotecas: `pip3 install --break-system-packages --upgrade <lib>`.

## Troubleshooting
- **MongoDB auth falla:** Verifica config en `/etc/mongod.conf`.
- **`mongosh` no conecta porque `mongod` no arranca:** Si el journal muestra `MongoDB cannot start: Linux kernel versions 6.19 and newer...`, es el kernel HWE 7.0, no la config de auth. Aplica la [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70).
- **Node-RED no inicia:** Revisa logs: `sudo journalctl -u nodered`.
- **Pip instala lento:** Usa mirror: `pip3 install --break-system-packages --index-url https://pypi.org/simple <lib>`.
- **`Cannot uninstall <paquete>, RECORD file not found`:** el paquete lo instaló `apt`, no pip, y aborta toda la transacción. Ver el recuadro del Paso 3.

> **Recursos Adicionales:**
> * [Node-RED Docs](https://nodered.org/docs/)
> * [MongoDB Docs](https://www.mongodb.com/docs/)
> * [Pandas Docs](https://pandas.pydata.org/docs/)

---

> [Índice](../README.md#índice) · [Anterior: 6. Configuración Específica para Estaciones de Compresión](06-estaciones-compresion.md) · [Siguiente: 8. Gestión de la Interfaz Gráfica](08-interfaz-grafica.md) · [English](en/07-analytics-workstations.md)
