import torch

print("PyTorch version :", torch.__version__)
print("CUDA disponible :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Nom du GPU :", torch.cuda.get_device_name(0))
    print("Nb de GPU :", torch.cuda.device_count())
    print("Mémoire GPU disponible :", torch.cuda.get_device_properties(0).total_memory / 1024**3, "GB")
else:
    print("⚠️ GPU CUDA non disponible. Vérifie le driver NVIDIA.")
