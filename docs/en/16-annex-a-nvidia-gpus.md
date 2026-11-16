# Annex A: Identifying NVIDIA GPUs

> [Index](../../README_en.md#index) · [Previous: FAQ: Frequently Asked Questions](15-faq.md) · [Next: Annex B: Compatibility Verification](17-annex-b-compatibility.md) · [Español](../16-anexo-a-gpus-nvidia.md)

> **Note:** To identify your GPU, run `lspci -nn | grep VGA` (shows Device ID in [xxxx:yyyy]). Search ID in tables below. If not found, use `nvidia-smi` if drivers installed.

## How to Identify
1. Run: `lspci -nn | grep VGA`
   - Example output: `01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA104 [GeForce RTX 3070] [10de:2484]`
   - Device ID: `2484` (last 4 digits).
2. Search ID in tables.
3. If NVIDIA, confirm with `nvidia-smi` (driver version).

## Simple Identification Script
Create `identify_gpu.sh`:
```bash
#!/bin/bash
echo "Searching NVIDIA GPUs..."
lspci -nn | grep -i nvidia | while read line; do
  device_id=$(echo $line | grep -oP '\[10de:\K[0-9a-f]{4}')
  model=$(echo $line | sed -n 's/.*NVIDIA Corporation \([^[]*\).*/\1/p')
  echo "Model: $model | Device ID: $device_id"
done
```
Run: `chmod +x identify_gpu.sh && ./identify_gpu.sh`

# NVIDIA GeForce RTX Series 3000 - PCI Identification (Ampere)

| Series | Model      | Device ID (hex) |
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

# NVIDIA GeForce RTX Series 4000 - PCI Identification (Ada Lovelace)

| Series | Model            | Device ID (hex) |
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

> **Note:** No desktop RTX 4050 exists; the "RTX 4050" name only ships in laptop/mobile variants. Always verify your Device ID with `lspci -nn | grep VGA` before assuming the model.

# NVIDIA GeForce RTX Series 5000 - PCI Identification (Blackwell)

> **Note:** These Device IDs are preliminary and may vary depending on the hardware revision. Verify with `lspci -nn | grep VGA` on your machine.

| Series | Model      | Device ID (hex) |
| ----- | ----------- | --------------- |
| 5000  | RTX 5090    | 2B80            |
| 5000  | RTX 5080    | 2B81            |
| 5000  | RTX 5070 Ti | 2B82            |
| 5000  | RTX 5070    | 2B83            |
| 5000  | RTX 5060 Ti | 2B84            |
| 5000  | RTX 5060    | 2B85            |

---

> [Index](../../README_en.md#index) · [Previous: FAQ: Frequently Asked Questions](15-faq.md) · [Next: Annex B: Compatibility Verification](17-annex-b-compatibility.md) · [Español](../16-anexo-a-gpus-nvidia.md)
