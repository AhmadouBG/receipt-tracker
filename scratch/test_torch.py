import torch
print(f"Torch version: {torch.__version__}")
try:
    import torchvision
    print(f"Torchvision version: {torchvision.__version__}")
except ImportError:
    print("Torchvision not installed")

x = torch.rand(5, 3)
print(x)
print("Import and basic tensor operation successful!")
