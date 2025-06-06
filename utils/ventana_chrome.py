import pygetwindow as gw
import pyautogui
import time
import subprocess

def abrir_y_posicionar_chrome(x=0, y=0, width=1280, height=720):
    try:
        # Intenta enfocar una ventana de Chrome existente
        ventanas = gw.getWindowsWithTitle("Chrome")
        if ventanas:
            ventana = ventanas[0]
            ventana.moveTo(x, y)
            ventana.resizeTo(width, height)
            ventana.activate()
            print(f"✔ Chrome reposicionado a {x},{y} con tamaño {width}x{height}")
            return True

        # Si no está abierto, lo abre
        print("🔄 Abriendo Google Chrome...")
        subprocess.Popen(["start", "chrome"], shell=True)
        time.sleep(3)  # Esperar a que abra

        ventanas = gw.getWindowsWithTitle("Chrome")
        if ventanas:
            ventana = ventanas[0]
            ventana.moveTo(x, y)
            ventana.resizeTo(width, height)
            ventana.activate()
            print(f"✔ Chrome reposicionado a {x},{y} con tamaño {width}x{height}")
            return True
        else:
            print("❌ No se pudo encontrar la ventana de Chrome.")
            return False
    except Exception as e:
        print(f"⚠ Error al mover Chrome: {e}")
        return False
