import platform
import subprocess
import os

def check_cpu():
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    try:
        # Check for AVX/AVX2 on Windows using wmic
        result = subprocess.run(['wmic', 'cpu', 'get', 'description'], capture_output=True, text=True)
        print(f"CPU Description: {result.stdout.strip()}")
    except Exception as e:
        print(f"Could not get CPU info: {e}")

if __name__ == "__main__":
    check_cpu()
