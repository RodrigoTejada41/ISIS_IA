# Instalacao Windows

```powershell
cd D:\ISIS_IA\AURORA
python -m pip install -e .[test]
python -m pytest
```

Opcionais:

```powershell
python -m pip install -e .[hardware]
```

Para VRAM real, instale driver NVIDIA com `nvidia-smi` no PATH.
