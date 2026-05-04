# test_hardware.py - Prueba de detección de hardware
import psutil
import platform

print("="*50)
print("PRUEBA DE DETECCIÓN DE HARDWARE")
print("="*50)

# RAM
ram = psutil.virtual_memory()
print(f"RAM Total: {round(ram.total / (1024**3), 1)} GB")
print(f"RAM Disponible: {round(ram.available / (1024**3), 1)} GB")
print(f"RAM Uso: {ram.percent}%")

# CPU Núcleos
print(f"Núcleos físicos: {psutil.cpu_count(logical=False)}")
print(f"Núcleos lógicos: {psutil.cpu_count(logical=True)}")

# CPU Frecuencia
try:
    freq = psutil.cpu_freq()
    if freq:
        print(f"Velocidad CPU: {round(freq.current / 1000, 1)} GHz")
    else:
        print("Velocidad CPU: No detectada")
except:
    print("Velocidad CPU: Error al detectar")

# CPU Uso
print(f"Uso CPU: {psutil.cpu_percent(interval=1)}%")

# Sistema
print(f"Sistema: {platform.system()}")
print(f"Versión: {platform.version()}")
print(f"Máquina: {platform.machine()}")

print("="*50)
