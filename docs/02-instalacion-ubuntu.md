# 2. Instalación del Sistema Ubuntu

> [Índice](../README.md#índice) · [Anterior: 1. Requisitos Previos a la Instalación](01-requisitos-previos.md) · [Siguiente: 3. Preparación Inicial del Sistema Ubuntu](03-preparacion-del-sistema.md) · [English](en/02-ubuntu-installation.md)

Esta sección deja Ubuntu instalado y listo para la preparación inicial. Sigue los pasos en orden.

## Paso 1: Descarga Ubuntu

1. Entra a [https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop).
2. Descarga la versión **Ubuntu Desktop LTS** indicada para tu instalación.
3. Guarda el archivo `.iso` en un lugar fácil de encontrar, por ejemplo `Downloads`.

> **Si el equipo va a correr MongoDB 8:** las ISO de Ubuntu Desktop 24.04.4 en adelante instalan
> el kernel **HWE 7.0**, que impide arrancar `mongod` (ver [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70)).
> La ISO de Ubuntu **Server** instala el track GA por defecto y no tiene el problema. Si igual
> instalas desde Desktop, aplica el pinning preventivo del [Paso 7 de la Sección 3](03-preparacion-del-sistema.md#paso-7-aplica-ajustes-según-tu-versión-de-ubuntu)
> antes de instalar MongoDB.

## Paso 2: Crea la USB de instalación

La forma más simple es usar una herramienta gráfica:

1. Descarga BalenaEtcher desde [https://etcher.balena.io/](https://etcher.balena.io/) o Ventoy desde [https://www.ventoy.net/](https://www.ventoy.net/).
2. Conecta la USB.
3. Selecciona la ISO de Ubuntu.
4. Selecciona la USB correcta.
5. Inicia el proceso y espera a que termine.

> **Cuidado:** La herramienta borrará la USB. Revisa dos veces que elegiste la unidad correcta.

## Paso 3: Entra a la BIOS/UEFI

1. Apaga el equipo.
2. Conecta la USB.
3. Enciende el equipo y presiona varias veces la tecla de BIOS.

Teclas comunes: `DEL`, `F2`, `F8`, `F10`, `F11`, `F12` o `ESC`.

Ejemplos habituales:

- ASUS suele usar `DEL`.
- MSI suele usar `DEL` o `F2`.
- Gigabyte suele usar `DEL`.

Si no entra, reinicia e intenta con otra tecla.

## Paso 4: Ajusta la BIOS/UEFI

Dentro de la BIOS, cambia solo lo necesario:

| Opción | Valor recomendado | Motivo |
|--------|-------------------|--------|
| Secure Boot | Disabled | Evita conflictos con drivers NVIDIA propietarios. |
| Boot Priority | USB primero | Permite arrancar el instalador de Ubuntu. |
| AC Power Loss | Always On, si es estación remota | El equipo vuelve a encender tras un corte de energía. |

Guarda los cambios con `F10` o con la opción **Save and Exit**.

## Paso 5: Arranca desde la USB

1. Al reiniciar, elige la USB como dispositivo de arranque.
2. Selecciona **Try or Install Ubuntu**.
3. Espera a que cargue el instalador.

Si aparece una pantalla negra antes de entrar al instalador, usa el modo `nomodeset`:

1. En el menú de arranque, presiona `E`.
2. Busca la línea que empieza con `linux`.
3. Agrega `nomodeset` al final de esa línea.
4. Presiona `F10` para continuar.

**Ejemplo de línea editada:**
```
linux /boot/vmlinuz-... nomodeset ---
```

## Paso 6: Instala Ubuntu con opciones simples

En el instalador, usa esta selección:

| Pantalla | Selección recomendada |
|----------|-----------------------|
| Idioma | **English**, para mantener nombres de carpetas estándar como `Desktop` y `Downloads`. |
| Teclado | Español o el layout físico del teclado. |
| Red | Conectado a internet si es posible. |
| Tipo de instalación | Normal installation. |
| Software adicional | Instala actualizaciones si el instalador lo ofrece. Si "software de terceros" mezcla gráficos y Wi-Fi, déjalo desmarcado; los drivers de red se revisan en la sección 3 y NVIDIA se instala luego con `.run`. |
| Disco | **Erase disk and install Ubuntu**, solo si ya respaldaste todo. |
| Usuario | Crea un usuario normal con contraseña fuerte. |
| Zona horaria | Selecciona la zona correcta. |

> **Alerta importante:** `Erase disk and install Ubuntu` borra el disco seleccionado. No elijas esa opción si necesitas conservar Windows, particiones o archivos.

La instalación puede tardar entre 15 y 30 minutos. Cuando termine, el instalador pedirá reiniciar.

## Paso 7: Primer inicio

1. Cuando Ubuntu lo pida, quita la USB.
2. Presiona `Enter` si aparece el mensaje de reinicio.
3. Inicia sesión con el usuario creado.
4. Abre una terminal con `Ctrl+Alt+T`.
5. Ejecuta estas verificaciones básicas:

```bash
lsb_release -a
ping -c 4 google.com
df -h
```

Resultado esperado:

- `lsb_release -a` muestra Ubuntu.
- `ping` recibe respuestas.
- `df -h` muestra espacio disponible en disco.

## Si algo falla durante la instalación

| Problema | Qué probar primero |
|----------|--------------------|
| La USB no aparece en el arranque | Rehacer la USB, probar otro puerto USB o revisar el orden de boot. |
| Pantalla negra antes del instalador | Arrancar con `nomodeset`. |
| El instalador se congela | Reiniciar, desactivar overclock en BIOS y volver a intentar. |
| No puedes desactivar Secure Boot | Revisar el manual de la placa madre o buscar el modelo exacto de BIOS. |
| Error al borrar o preparar disco | Usar la opción simple si no necesitas dual boot; si necesitas dual boot, detenerse y preparar particiones manualmente. |
| No hay internet | Continuar la instalación y resolver red después en la sección de problemas de red. |

---

> [Índice](../README.md#índice) · [Anterior: 1. Requisitos Previos a la Instalación](01-requisitos-previos.md) · [Siguiente: 3. Preparación Inicial del Sistema Ubuntu](03-preparacion-del-sistema.md) · [English](en/02-ubuntu-installation.md)
