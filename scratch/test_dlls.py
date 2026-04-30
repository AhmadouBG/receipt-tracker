import ctypes
import os

torch_lib_path = r"C:\Users\Bamba\Documents\receipt-tracker\venv\Lib\site-packages\torch\lib"
os.add_dll_directory(torch_lib_path)

dlls_to_test = [
    "libiomp5md.dll",
    "c10.dll",
    "torch_cpu.dll"
]

for dll_name in dlls_to_test:
    dll_path = os.path.join(torch_lib_path, dll_name)
    print(f"\nTesting {dll_name}...")
    try:
        # LoadLibraryExW with LOAD_LIBRARY_SEARCH_DEFAULT_DIRS | LOAD_LIBRARY_SEARCH_USER_DIRS
        ctypes.WinDLL(dll_path)
        print(f"SUCCESS: Loaded {dll_name}")
    except OSError as e:
        print(f"FAILED: Could not load {dll_name}. Error: {e}")
