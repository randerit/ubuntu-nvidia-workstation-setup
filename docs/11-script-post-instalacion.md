# 11. Script de Post-Instalación (Opcional)

> [Índice](../README.md#índice) · [Anterior: 10. Wake-on-LAN (WOL): Windows a Windows y Ubuntu a Windows](10-wake-on-lan.md) · [Siguiente: 12. Scripts Doctor de Verificación](12-scripts-doctor.md) · [English](en/11-post-install-script.md)

> **Nota:** Este script automatiza la preparación inicial (sección 3). Actualízalo según tus necesidades. Ejecuta como root o con sudo.

## Script Mejorado `setup.sh`
Incluye dependencias adicionales y opciones.

```bash
#!/bin/bash
# Script para la preparación inicial del sistema Ubuntu
# Versión mejorada con más herramientas

set -euo pipefail  # Salir en error, variables no definidas, y fallos en pipes

echo "--- Actualizando el sistema ---"
sudo apt update && sudo apt upgrade -y

echo "--- Instalando dependencias comunes ---"
sudo apt install -y build-essential dkms pkg-config libglvnd-dev libgl1-mesa-dev libegl1-mesa-dev libgles2-mesa-dev libx11-dev libxmu-dev libxi-dev libglu1-mesa-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev mesa-utils inxi net-tools openssh-server curl git wget htop ncdu tree traceroute nmap vim lm-sensors neofetch

echo "--- Configurando GDM3 (desactivar Wayland) ---"
if [ -f /etc/gdm3/custom.conf ]; then
  sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf
else
  echo "Archivo /etc/gdm3/custom.conf no encontrado. Omitiendo configuración de Wayland."
fi

echo "--- Configurando firewall (opcional) ---"
read -r -p "¿Habilitar UFW con SSH? (s/n): " ufw_choice
if [[ $ufw_choice =~ ^[sS]$ ]]; then
  sudo ufw allow ssh
  sudo ufw --force enable
fi

echo "--- Verificaciones ---"
echo "GCC versión: $(gcc --version | head -1)"
echo "Git versión: $(git --version)"
echo "Firewall status: $(sudo ufw status | head -1)"

echo "--- Preparación completada. Reinicio recomendado. ---"
read -r -p "¿Reiniciar ahora? (s/n): " choice
case "$choice" in
  s|S ) sudo reboot;;
  * ) echo "Ejecuta 'sudo reboot' manualmente.";;
esac
```

## Cómo Usarlo
1. Crea el archivo: `nano setup.sh`
2. Pega el contenido y guarda.
3. Permisos: `chmod +x setup.sh`
4. Ejecuta: `./setup.sh` (o `sudo ./setup.sh` si necesita root)

## Personalización
- Agrega más installs: `sudo apt install -y <paquete>`
- Quita opciones: Comenta líneas con `#`
- Logging: Agrega `>> setup.log` a comandos.

## Troubleshooting
- Si falla: Revisa logs en terminal.
- Permisos: Asegura que el script tenga ejecución.
- Dependencias: Verifica internet para apt.

---

> [Índice](../README.md#índice) · [Anterior: 10. Wake-on-LAN (WOL): Windows a Windows y Ubuntu a Windows](10-wake-on-lan.md) · [Siguiente: 12. Scripts Doctor de Verificación](12-scripts-doctor.md) · [English](en/11-post-install-script.md)
