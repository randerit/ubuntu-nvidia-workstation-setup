# FAQ: Preguntas Frecuentes

> [Índice](../README.md#índice) · [Anterior: 14. Runbook: MongoDB 8 no arranca por kernel HWE 7.0](14-runbook-mongodb8-kernel.md) · [Siguiente: Anexo A: Identificación de GPUs NVIDIA](16-anexo-a-gpus-nvidia.md) · [English](en/15-faq.md)

* **¿Qué hago si el driver NVIDIA no se instala correctamente?**
  * Revisa la compatibilidad en el Anexo B y asegúrate de haber eliminado drivers antiguos. Ejecuta `sudo apt purge nvidia*` y reinicia antes de reinstalar.

* **¿Cómo sé qué versión de CUDA instalar?**
  * Consulta la web oficial y verifica compatibilidad con tu GPU. Para este manual, mantén el driver en la rama 580.x.x y elige CUDA compatible con esa rama.

* **¿Por qué no funciona Wake-on-LAN?**
  * Verifica configuración de BIOS, opciones de energía y que el equipo esté conectado por cable. Ejecuta `sudo ethtool enpXsY` para checkear soporte WOL.

* **¿Puedo usar esta guía en variantes de Ubuntu?**
  * Sí, pero puede haber diferencias menores. Se recomienda Ubuntu Desktop. Para Server, omite secciones GUI.

* **¿Cómo verifico si mi GPU es compatible?**
  * Usa `lspci -nn | grep VGA` para el Device ID, luego busca en Anexo A. Confirma con `nvidia-smi` después de instalar drivers.

* **¿Qué pasa si CUDA no reconoce la GPU?**
  * Asegúrate de que drivers estén instalados correctamente (`nvidia-smi`). Reinicia si es necesario. Verifica compatibilidad en Anexo B.

* **¿Por qué la pantalla queda negra después de instalar drivers?**
  * Agrega `nomodeset` en GRUB (sección 2). Si usas GDM3, fuerza Xorg en `/etc/gdm3/custom.conf`.

* **¿Cómo configuro red en placas nuevas?**
  * Identifica el chip con `lspci | grep Network`, instala drivers apropiados (ej. `sudo apt install r8168-dkms` para Realtek).

* **¿Puedo usar Docker con NVIDIA GPUs?**
  * Sí, instala `nvidia-container-toolkit` (reemplaza al deprecado `nvidia-docker2`). Sigue la [guía oficial](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html), reinicia Docker con `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`, y ejecuta contenedores con `docker run --gpus all`.

* **¿Cómo libero memoria GPU para otras apps?**
  * Desactiva entorno gráfico: `sudo systemctl set-default multi-user.target && sudo reboot`. Reactiva con `graphical.target`.

* **¿Qué hago si MongoDB o Node-RED no inician?**
  * Revisa logs: `sudo journalctl -u mongod` o `sudo journalctl -u nodered`. Verifica puertos con `sudo netstat -tlnp`.

* **`mongod` no arranca y el log habla de "Linux kernel versions 6.19 and newer". ¿Qué pasa?**
  * El equipo está en el kernel HWE 7.0 y MongoDB 8 se niega a arrancar en el rango 6.19 – 7.0.13 ([SERVER-121912](https://jira.mongodb.org/browse/SERVER-121912)). No es config de MongoDB: hay que volver al track GA 6.8. Sigue la [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70).

* **¿Cómo actualizo el kernel sin romper drivers?**
  * Actualiza normalmente: `sudo apt update && sudo apt upgrade`. Si hay issues, reinstala drivers después. **Excepción:** en equipos con MongoDB 8 no instales el kernel HWE (`linux-generic-hwe-24.04`); quédate en el track GA 6.8 con el pinning de la [Sección 14](14-runbook-mongodb8-kernel.md#14-runbook-mongodb-8-no-arranca-por-kernel-hwe-70). El track GA sigue recibiendo parches de seguridad hasta el fin de vida de 24.04.

* **¿Por qué `uname -r` muestra `7.0.0-XX` si Canonical ya publicó el kernel corregido?**
  * Ubuntu mantiene fijo el `X.Y.0-ABI` en `uname -r` y solo sube el número de ABI, aunque internamente rebase el sublevel upstream. El guard de MongoDB lee ese string, así que seguirá bloqueando incluso sobre un kernel ya parcheado. Revisa la base real con `cat /proc/version_signature`.

* **¿Es seguro usar el script post-install?**
  * Revisa el código antes de ejecutar. Hace backups y configura según la guía, pero úsalo con precaución en producción.

* **¿Dónde encuentro logs de errores?**
  * Drivers: `/var/log/nvidia-installer.log`. Sistema: `sudo journalctl -xe`. CUDA: logs en `/var/log/cuda-installer.log`.

* **¿Cómo desinstalo todo NVIDIA para reinstalar?**
  * Ejecuta `sudo apt purge nvidia* cuda*`, elimina `/usr/local/cuda*`, reinicia y sigue la guía desde cero.

---

> [Índice](../README.md#índice) · [Anterior: 14. Runbook: MongoDB 8 no arranca por kernel HWE 7.0](14-runbook-mongodb8-kernel.md) · [Siguiente: Anexo A: Identificación de GPUs NVIDIA](16-anexo-a-gpus-nvidia.md) · [English](en/15-faq.md)
