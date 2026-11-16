# Anexo A: Identificación de GPUs NVIDIA

> [Índice](../README.md#índice) · [Anterior: FAQ: Preguntas Frecuentes](15-faq.md) · [Siguiente: Anexo B: Verificación de Compatibilidad](17-anexo-b-compatibilidad.md) · [English](en/16-annex-a-nvidia-gpus.md)

> **Nota:** Para identificar tu GPU, ejecuta `lspci -nn | grep VGA` (muestra Device ID en [xxxx:yyyy]). Busca el ID en las tablas abajo. Si no encuentras, usa `nvidia-smi` si drivers están instalados.

## Cómo Identificar
1. Ejecuta: `lspci -nn | grep VGA`
   - Ejemplo salida: `01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA104 [GeForce RTX 3070] [10de:2484]`
   - Device ID: `2484` (últimos 4 dígitos).
2. Busca el ID en las tablas.
3. Si es NVIDIA, confirma con `nvidia-smi` (versión driver).

## Script Simple para Identificación
Crea `identify_gpu.sh`:
```bash
#!/bin/bash
echo "Buscando GPUs NVIDIA..."
lspci -nn | grep -i nvidia | while read line; do
  device_id=$(echo $line | grep -oP '\[10de:\K[0-9a-f]{4}')
  model=$(echo $line | sed -n 's/.*NVIDIA Corporation \([^[]*\).*/\1/p')
  echo "Modelo: $model | Device ID: $device_id"
done
```
Ejecuta: `chmod +x identify_gpu.sh && ./identify_gpu.sh`

# NVIDIA GeForce RTX Serie 3000 - Identificación PCI (Ampere)

| Serie | Modelo      | Device ID (hex) |
| ----- | ----------- | --------------- |
| 3000  | RTX 3090    | 2204            |
| 3000  | RTX 3090 Ti | 22C6            |
| 3000  | RTX 3080    | 2206            |
| 3000  | RTX 3080 Ti | 2382            |
| 3000  | RTX 3070 Ti | 24C0            |
| 3000  | RTX 3070    | 2484            |
| 3000  | RTX 3060 Ti | 2489            |
| 3000  | RTX 3060    | 2503            |
| 3000  | RTX 3050 Ti | 2191            |
| 3000  | RTX 3050    | 25A0            |

# NVIDIA GeForce RTX Serie 4000 - Identificación PCI (Ada Lovelace)

| Serie | Modelo            | Device ID (hex) |
| ----- | ----------------- | --------------- |
| 4000  | RTX 4090          | 2684            |
| 4000  | RTX 4080 Super    | 2702            |
| 4000  | RTX 4080          | 2704            |
| 4000  | RTX 4070 Ti Super | 26B0            |
| 4000  | RTX 4070 Ti       | 2782            |
| 4000  | RTX 4070 Super    | 2788            |
| 4000  | RTX 4070          | 2786            |
| 4000  | RTX 4060 Ti       | 28A3            |
| 4000  | RTX 4060          | 2882            |

> **Nota:** No existe RTX 4050 de escritorio; "RTX 4050" solo se comercializa en variantes laptop/mobile. Verifica siempre tu Device ID con `lspci -nn | grep VGA` antes de asumir el modelo.

# NVIDIA GeForce RTX Serie 5000 - Identificación PCI (Blackwell)

> **Nota:** Estos Device IDs son preliminares y pueden variar según la revisión del hardware. Verifica con `lspci -nn | grep VGA` en tu equipo.

| Serie | Modelo      | Device ID (hex) |
| ----- | ----------- | --------------- |
| 5000  | RTX 5090    | 2B80            |
| 5000  | RTX 5080    | 2B81            |
| 5000  | RTX 5070 Ti | 2B82            |
| 5000  | RTX 5070    | 2B83            |
| 5000  | RTX 5060 Ti | 2B84            |
| 5000  | RTX 5060    | 2B85            |

---

> [Índice](../README.md#índice) · [Anterior: FAQ: Preguntas Frecuentes](15-faq.md) · [Siguiente: Anexo B: Verificación de Compatibilidad](17-anexo-b-compatibilidad.md) · [English](en/16-annex-a-nvidia-gpus.md)
