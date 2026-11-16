# 8. Gestión de la Interfaz Gráfica

> [Índice](../README.md#índice) · [Anterior: 7. Configuración Específica para Estaciones de Analítica](07-estaciones-analitica.md) · [Siguiente: 9. Solución de Problemas Comunes con Redes en Placas Nuevas](09-redes-placas-nuevas.md) · [English](en/08-graphical-interface.md)

> **Nota:** Ubuntu usa GDM3 como display manager. Gestiona el entorno gráfico para liberar recursos en servidores o solucionar issues con GPUs.

## Verificar Estado Actual
Antes de cambiar, checkea el target actual:
```bash
systemctl get-default  # Debería mostrar graphical.target o multi-user.target
who  # Muestra sesiones activas
```

## Desactivar Entorno Gráfico (Modo Texto/Servidor)
Útil para servidores headless o troubleshooting.

### Paso 1: Deshabilita GDM3
```bash
sudo systemctl disable gdm3
sudo systemctl set-default multi-user.target
```

### Paso 2: Reinicia
```bash
sudo reboot
```

**Verificación (opcional):**
```bash
systemctl get-default  # multi-user.target
# No verás entorno gráfico al bootear
```

## Reactivar Entorno Gráfico
Para uso desktop normal.

### Paso 1: Habilita GDM3
```bash
sudo systemctl enable gdm3
sudo systemctl set-default graphical.target
```

### Paso 2: Reinicia
```bash
sudo reboot
```

**Verificación (opcional):**
```bash
systemctl get-default  # graphical.target
# Deberías ver login gráfico
```

## Alternativas y Tips
- **Cambiar sin reinicio:** Usa `sudo systemctl isolate multi-user.target` (temporal).
- **Otro DM:** Si prefieres LightDM: `sudo apt install lightdm && sudo dpkg-reconfigure lightdm`.
- **Issues con GPUs:** Si pantalla negra, fuerza Xorg en `/etc/gdm3/custom.conf` (ver sección 3).

## Troubleshooting
- **GDM3 no inicia:** Logs: `sudo journalctl -u gdm`.
- **Pantalla negra:** Agrega `nomodeset` en GRUB (ver sección 2).
- **No cambia target:** `sudo systemctl daemon-reload` y reintenta.

> **Explicación:** Desactivar libera RAM/CPU; reactivar para apps GUI. Usa según necesidad.

---

> [Índice](../README.md#índice) · [Anterior: 7. Configuración Específica para Estaciones de Analítica](07-estaciones-analitica.md) · [Siguiente: 9. Solución de Problemas Comunes con Redes en Placas Nuevas](09-redes-placas-nuevas.md) · [English](en/08-graphical-interface.md)
